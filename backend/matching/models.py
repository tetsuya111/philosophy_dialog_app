from typing import ClassVar

from django.db import models

from accounts.models import CustomUser


class GuestClient(models.Model):
    """ログインなしの利用者。利用者識別子1つにつきゲスト用のCustomUserを1つ持つ。"""

    user = models.OneToOneField(CustomUser, related_name="guest_client", on_delete=models.CASCADE)
    client_id_hash = models.CharField(max_length=64, unique=True, db_comment="利用者識別子のSHA-256")
    created_at = models.DateTimeField(auto_now_add=True, db_comment="作成日時")

    def __str__(self) -> str:
        return f"GuestClient({self.user_id})"


class WaitingQueue(models.Model):
    """待機列の1エントリ。userはOneToOneなので二重参加はDBレベルで起きない。"""

    user = models.OneToOneField(CustomUser, related_name="waiting", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, db_comment="作成日時")  # FIFOの順序・タイムアウトの起点

    class Meta:
        ordering: ClassVar = ["created_at", "id"]

    def __str__(self) -> str:
        return f"WaitingQueue({self.user_id})"


class Room(models.Model):
    """マッチングで作られたグループ。1つのJitsiルームと有効期限を持つ。"""

    class Status(models.TextChoices):
        ACTIVE = "active"
        ENDED = "ended"

    class EndReason(models.TextChoices):
        ALL_LEFT = "all_left"  # 全メンバーが満了前に通話終了した
        EXPIRED = "expired"  # 有効時間の満了

    room_name = models.CharField(max_length=64, unique=True, db_comment="Jitsiのルーム名")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE, db_comment="状態")
    end_reason = models.CharField(max_length=10, choices=EndReason.choices, blank=True, db_comment="終了理由")
    created_at = models.DateTimeField(auto_now_add=True, db_comment="作成日時")
    expires_at = models.DateTimeField(db_comment="有効期限")
    ended_at = models.DateTimeField(null=True, blank=True, db_comment="終了日時")

    class Meta:
        indexes: ClassVar = [models.Index(fields=["status", "expires_at"])]

    def __str__(self) -> str:
        return f"Room({self.pk}, {self.status})"


class RoomMember(models.Model):
    """グループのメンバー。is_active=Trueの行がユーザーを「マッチング済み」「通話中」として拘束する。"""

    room = models.ForeignKey(Room, related_name="members", on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, related_name="room_memberships", on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True, db_comment="このメンバー行が現在ユーザーを拘束しているか")
    joined_at = models.DateTimeField(null=True, blank=True, db_comment="初回入室日時")
    left_at = models.DateTimeField(null=True, blank=True, db_comment="満了前の通話終了日時")

    class Meta:
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["room", "user"], name="unique_room_member"),
            # 1ユーザーが同時に複数の未終了グループに属さない
            models.UniqueConstraint(fields=["user"], condition=models.Q(is_active=True), name="one_active_room_per_user"),
        ]

    def __str__(self) -> str:
        return f"RoomMember({self.room_id}, {self.user_id})"
