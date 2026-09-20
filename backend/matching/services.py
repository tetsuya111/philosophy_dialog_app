"""ランダムコールの状態を変える処理をすべて集約する(.kiro/specs/random-call/design.md)。

各関数は transaction.atomic() の中で対象行を select_for_update() してから判定・更新する。
SQLiteでは select_for_update() は無効だが、書き込みトランザクションがDBファイル単位で直列化されるため整合性は保たれる。
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import TYPE_CHECKING

import structlog
from django.db import IntegrityError, transaction
from django.utils import timezone

from accounts.models import CustomUser

from .authentication import hash_client_id
from .constants import GROUP_SIZE, QUEUE_TIMEOUT, ROOM_NAME_PREFIX, ROOM_TTL
from .models import GuestClient, Room, RoomMember, WaitingQueue

if TYPE_CHECKING:
    from datetime import datetime

logger = structlog.get_logger("matching")


class State:
    """ユーザーの状態。DBには保存せず、待機列・メンバー行の有無から導出する。"""

    NONE = "none"
    WAITING = "waiting"
    MATCHED = "matched"
    IN_CALL = "in_call"


class AlreadyInRoomError(Exception):
    """マッチング済み・通話中のユーザーが待機列に参加しようとした。"""


class NotWaitingError(Exception):
    """待機中でないユーザーが待機の取りやめを要求した。"""


class NotInRoomError(Exception):
    """未終了のグループに属していない。"""


class RoomEndedError(Exception):
    """グループが終了済み(有効時間の満了)。"""


@dataclass(frozen=True)
class UserState:
    status: str
    waiting: WaitingQueue | None = None
    room: Room | None = None


def issue_client() -> str:
    """ゲスト用ユーザーを作成し、平文の利用者識別子を返す。DBにはハッシュのみ保存する。"""
    client_id = secrets.token_urlsafe(32)
    with transaction.atomic():
        user = CustomUser(username="guest-" + secrets.token_hex(16))
        user.set_unusable_password()
        user.save()
        GuestClient.objects.create(user=user, client_id_hash=hash_client_id(client_id))
    logger.info("client_issued", user_id=user.pk)
    return client_id


def get_state(user: CustomUser) -> UserState:
    waiting = WaitingQueue.objects.filter(user=user).first()
    if waiting is not None:
        return UserState(State.WAITING, waiting=waiting)
    member = RoomMember.objects.select_related("room").filter(user=user, is_active=True).first()
    if member is None:
        return UserState(State.NONE)
    status = State.MATCHED if member.joined_at is None else State.IN_CALL
    return UserState(status, room=member.room)


def join_queue(user: CustomUser) -> None:
    """待機列に参加する。既に待機中なら何もしない。参加後に4人揃っていればグループを作る。"""
    with transaction.atomic():
        if RoomMember.objects.filter(user=user, is_active=True).exists():
            raise AlreadyInRoomError
        _, created = WaitingQueue.objects.get_or_create(user=user)
    if created:
        logger.info("queue_joined", user_id=user.pk)
        while try_form_group() is not None:
            pass


def cancel_queue(user: CustomUser) -> None:
    """ユーザー自身の元の待機エントリを削除する。"""
    with transaction.atomic():
        waiting = WaitingQueue.objects.select_for_update().filter(user=user).first()
        if waiting is None:
            # 同時にマッチング成立・タイムアウトで消えていた場合を含む
            raise NotWaitingError
        waiting.delete()
    logger.info("queue_cancelled", user_id=user.pk)


def try_form_group() -> Room | None:
    """待機列の先頭 GROUP_SIZE 人が揃っていれば1つのグループにまとめる。"""
    try:
        room, user_ids = _form_group()
    except IntegrityError:
        # 制約違反(同一ユーザーの二重所属)はトランザクションごとロールバックされ、待機列はそのまま残る
        logger.exception("room_form_failed")
        return None
    if room is not None:
        logger.info("room_formed", room_id=room.pk, user_ids=user_ids)
    return room


def _form_group() -> tuple[Room | None, list[int]]:
    with transaction.atomic():
        entries = list(WaitingQueue.objects.select_for_update().select_related("user").order_by("created_at", "id")[:GROUP_SIZE])
        if len(entries) < GROUP_SIZE:
            return None, []
        now = timezone.now()
        room = Room.objects.create(room_name=ROOM_NAME_PREFIX + secrets.token_hex(16), expires_at=now + ROOM_TTL)
        RoomMember.objects.bulk_create([RoomMember(room=room, user=entry.user) for entry in entries])
        WaitingQueue.objects.filter(pk__in=[entry.pk for entry in entries]).delete()
    return room, [entry.user.pk for entry in entries]


def _lock_active_member(user: CustomUser) -> RoomMember | None:
    member = RoomMember.objects.select_for_update().filter(user=user, is_active=True).first()
    if member is None:
        return None
    # グループ行もロックし、満了処理・他メンバーの退室と直列化する
    member.room = Room.objects.select_for_update().get(pk=member.room_id)
    return member


def enter_call(user: CustomUser) -> Room:
    """通話ルームへの入室を記録し「通話中」にする。再入室では joined_at を変えない。"""
    with transaction.atomic():
        member = _lock_active_member(user)
        if member is None:
            raise NotInRoomError
        room = member.room
        if room.expires_at <= timezone.now():
            _end_room(room, Room.EndReason.EXPIRED)
            expired = True
        else:
            expired = False
            if member.joined_at is None:
                member.joined_at = timezone.now()
                member.save(update_fields=["joined_at"])
    if expired:
        # 満了による終了はコミットしたうえで拒否する
        raise RoomEndedError
    logger.info("call_entered", user_id=user.pk, room_id=room.pk)
    return room


def leave_call(user: CustomUser) -> None:
    """ユーザー自身の通話終了を記録する。未所属・終了済みなら何もしない。"""
    with transaction.atomic():
        member = _lock_active_member(user)
        if member is None:
            return
        room = member.room
        if room.expires_at <= timezone.now():
            # 満了済みなら通話終了ではなく満了として扱う
            _end_room(room, Room.EndReason.EXPIRED)
            return
        member.left_at = timezone.now()
        member.is_active = False
        member.save(update_fields=["left_at", "is_active"])
        logger.info("call_left", user_id=user.pk, room_id=room.pk)
        if not room.members.filter(is_active=True).exists():
            _end_room(room, Room.EndReason.ALL_LEFT)


def _end_room(room: Room, reason: str) -> None:
    """グループを終了し、全メンバーの拘束を解く。呼び出し元でroom行をロックしていること。"""
    room.status = Room.Status.ENDED
    room.end_reason = reason
    room.ended_at = timezone.now()
    room.save(update_fields=["status", "end_reason", "ended_at"])
    room.members.filter(is_active=True).update(is_active=False)
    logger.info("room_ended", room_id=room.pk, reason=reason)


def expire_stale(now: datetime | None = None) -> tuple[int, int]:
    """タイムアウトした待機エントリと、有効期限を過ぎたグループを処理する。

    呼び出したユーザーに限らず全体が対象。対象がなければ書き込みを行わない(SQLiteのロック競合を抑えるため)。
    戻り値は(タイムアウトした待機エントリ数, 満了で終了したグループ数)。
    """
    now = now or timezone.now()
    timed_out = 0
    deadline = now - QUEUE_TIMEOUT
    if WaitingQueue.objects.filter(created_at__lte=deadline).exists():
        with transaction.atomic():
            timed_out, _ = WaitingQueue.objects.select_for_update().filter(created_at__lte=deadline).delete()
        logger.info("queue_timed_out", count=timed_out)

    expired = 0
    room_ids = list(Room.objects.filter(status=Room.Status.ACTIVE, expires_at__lte=now).values_list("pk", flat=True))
    for room_id in room_ids:
        with transaction.atomic():
            room = Room.objects.select_for_update().filter(pk=room_id, status=Room.Status.ACTIVE).first()
            if room is None:
                # 同時に別のリクエストが終了させていた
                continue
            _end_room(room, Room.EndReason.EXPIRED)
            expired += 1
    return timed_out, expired
