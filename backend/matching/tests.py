from __future__ import annotations

from datetime import timedelta

from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import CustomUser

from . import services
from .authentication import hash_client_id
from .constants import GROUP_SIZE, QUEUE_TIMEOUT, ROOM_TTL
from .models import GuestClient, Room, RoomMember, WaitingQueue
from .services import State


def new_guest() -> tuple[str, CustomUser]:
    client_id = services.issue_client()
    return client_id, GuestClient.objects.get(client_id_hash=hash_client_id(client_id)).user


def expire_room(room: Room) -> None:
    Room.objects.filter(pk=room.pk).update(expires_at=timezone.now() - timedelta(seconds=1))


class ServiceTestCase(TestCase):
    def setUp(self) -> None:
        self.users = [new_guest()[1] for _ in range(GROUP_SIZE + 1)]

    def fill_group(self) -> Room:
        for user in self.users[:GROUP_SIZE]:
            services.join_queue(user)
        return Room.objects.get()

    def test_issue_client_stores_only_hash(self) -> None:
        client_id, user = new_guest()
        guest = GuestClient.objects.get(user=user)
        self.assertNotEqual(guest.client_id_hash, client_id)
        self.assertFalse(GuestClient.objects.filter(client_id_hash=client_id).exists())
        self.assertFalse(user.has_usable_password())

    def test_join_makes_waiting_and_is_idempotent(self) -> None:
        user = self.users[0]
        services.join_queue(user)
        services.join_queue(user)
        self.assertEqual(WaitingQueue.objects.filter(user=user).count(), 1)
        self.assertEqual(services.get_state(user).status, State.WAITING)

    def test_no_group_until_group_size(self) -> None:
        for user in self.users[: GROUP_SIZE - 1]:
            services.join_queue(user)
        self.assertFalse(Room.objects.exists())

    def test_group_formed_fifo_and_fifth_keeps_waiting(self) -> None:
        for user in self.users:
            services.join_queue(user)
        room = Room.objects.get()
        member_ids = set(room.members.values_list("user_id", flat=True))
        self.assertEqual(member_ids, {u.pk for u in self.users[:GROUP_SIZE]})
        self.assertTrue(room.room_name.startswith("pd-"))
        self.assertAlmostEqual(room.expires_at, room.created_at + ROOM_TTL, delta=timedelta(seconds=1))
        for user in self.users[:GROUP_SIZE]:
            self.assertEqual(services.get_state(user).status, State.MATCHED)
        self.assertEqual(services.get_state(self.users[GROUP_SIZE]).status, State.WAITING)

    def test_join_rejected_when_matched(self) -> None:
        self.fill_group()
        with self.assertRaises(services.AlreadyInRoomError):
            services.join_queue(self.users[0])

    def test_cancel_deletes_own_entry(self) -> None:
        user = self.users[0]
        services.join_queue(user)
        services.cancel_queue(user)
        self.assertFalse(WaitingQueue.objects.filter(user=user).exists())
        self.assertEqual(services.get_state(user).status, State.NONE)

    def test_cancel_after_matching_is_rejected(self) -> None:
        # 取りやめとマッチング成立が競合し、成立が先だった場合
        self.fill_group()
        with self.assertRaises(services.NotWaitingError):
            services.cancel_queue(self.users[0])
        self.assertEqual(services.get_state(self.users[0]).status, State.MATCHED)

    def test_queue_timeout(self) -> None:
        user = self.users[0]
        services.join_queue(user)
        WaitingQueue.objects.filter(user=user).update(created_at=timezone.now() - QUEUE_TIMEOUT)
        self.assertEqual(services.expire_stale(), (1, 0))
        self.assertEqual(services.get_state(user).status, State.NONE)

    def test_timeout_after_matching_does_nothing(self) -> None:
        self.fill_group()
        self.assertEqual(services.expire_stale(), (0, 0))
        self.assertEqual(services.get_state(self.users[0]).status, State.MATCHED)

    def test_enter_and_reenter_keeps_joined_at(self) -> None:
        self.fill_group()
        user = self.users[0]
        services.enter_call(user)
        joined_at = RoomMember.objects.get(user=user).joined_at
        self.assertIsNotNone(joined_at)
        self.assertEqual(services.get_state(user).status, State.IN_CALL)
        services.enter_call(user)
        self.assertEqual(RoomMember.objects.get(user=user).joined_at, joined_at)

    def test_enter_without_room(self) -> None:
        with self.assertRaises(services.NotInRoomError):
            services.enter_call(self.users[0])

    def test_enter_after_expiry(self) -> None:
        room = self.fill_group()
        expire_room(room)
        with self.assertRaises(services.RoomEndedError):
            services.enter_call(self.users[0])
        room.refresh_from_db()
        self.assertEqual(room.end_reason, Room.EndReason.EXPIRED)
        self.assertEqual(services.get_state(self.users[0]).status, State.NONE)

    def test_leave_returns_to_none_and_room_continues(self) -> None:
        room = self.fill_group()
        user = self.users[0]
        services.enter_call(user)
        services.leave_call(user)
        self.assertEqual(services.get_state(user).status, State.NONE)
        self.assertIsNotNone(RoomMember.objects.get(user=user).left_at)
        room.refresh_from_db()
        self.assertEqual(room.status, Room.Status.ACTIVE)
        # 退室後はすぐ待機列に再参加できる
        services.join_queue(user)
        self.assertEqual(services.get_state(user).status, State.WAITING)

    def test_all_left_ends_room(self) -> None:
        room = self.fill_group()
        for user in self.users[:GROUP_SIZE]:
            services.leave_call(user)
        room.refresh_from_db()
        self.assertEqual(room.status, Room.Status.ENDED)
        self.assertEqual(room.end_reason, Room.EndReason.ALL_LEFT)

    def test_leave_without_room_does_nothing(self) -> None:
        services.leave_call(self.users[0])
        self.assertEqual(services.get_state(self.users[0]).status, State.NONE)

    def test_expiry_ends_room_and_releases_members(self) -> None:
        room = self.fill_group()
        services.enter_call(self.users[0])
        expire_room(room)
        self.assertEqual(services.expire_stale(), (0, 1))
        room.refresh_from_db()
        self.assertEqual(room.end_reason, Room.EndReason.EXPIRED)
        for user in self.users[:GROUP_SIZE]:
            self.assertEqual(services.get_state(user).status, State.NONE)
        # 満了は通話終了として記録しない
        self.assertIsNone(RoomMember.objects.get(user=self.users[0]).left_at)

    def test_leave_after_expiry_is_treated_as_expiry(self) -> None:
        room = self.fill_group()
        services.enter_call(self.users[0])
        expire_room(room)
        services.leave_call(self.users[0])
        room.refresh_from_db()
        self.assertEqual(room.end_reason, Room.EndReason.EXPIRED)
        self.assertIsNone(RoomMember.objects.get(user=self.users[0]).left_at)

    def test_one_active_room_per_user_constraint(self) -> None:
        room = self.fill_group()
        other = Room.objects.create(room_name="pd-other", expires_at=room.expires_at)
        with self.assertRaises(IntegrityError), transaction.atomic():
            RoomMember.objects.create(room=other, user=self.users[0])


class APITestCase(TestCase):
    def setUp(self) -> None:
        cache.clear()  # レート制限のカウンタをテストごとにリセットする
        self.api = APIClient()

    def client_for(self, client_id: str) -> APIClient:
        api = APIClient()
        api.credentials(HTTP_X_CLIENT_ID=client_id)
        return api

    def test_issue_client(self) -> None:
        res = self.api.post("/api/matching/client/")
        self.assertEqual(res.status_code, 201)
        client_id = res.json()["client_id"]
        res = self.client_for(client_id).get("/api/matching/status/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], State.NONE)

    def test_issue_client_is_throttled(self) -> None:
        codes = [self.api.post("/api/matching/client/").status_code for _ in range(31)]
        self.assertEqual(codes[:30], [201] * 30)
        self.assertEqual(codes[30], 429)

    def test_requires_client_id(self) -> None:
        self.assertEqual(self.api.get("/api/matching/status/").status_code, 401)
        self.assertEqual(self.client_for("unknown").get("/api/matching/status/").status_code, 401)
        self.assertEqual(self.api.post("/api/matching/join/").status_code, 401)

    def test_state_changing_endpoints_reject_get(self) -> None:
        api = self.client_for(new_guest()[0])
        for path in ("join/", "cancel/", "call/enter/", "call/leave/"):
            self.assertEqual(api.get("/api/matching/" + path).status_code, 405, path)
        self.assertFalse(WaitingQueue.objects.exists())

    def test_join_cancel_flow(self) -> None:
        api = self.client_for(new_guest()[0])
        res = api.post("/api/matching/join/")
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertEqual(body["status"], State.WAITING)
        self.assertIn("expires_at", body["waiting"])
        self.assertIn("server_time", body)
        res = api.post("/api/matching/cancel/")
        self.assertEqual(res.json()["status"], State.NONE)
        res = api.post("/api/matching/cancel/")
        self.assertEqual(res.status_code, 409)
        self.assertEqual(res.json()["status"], State.NONE)

    def test_matching_enter_leave_flow(self) -> None:
        apis = [self.client_for(new_guest()[0]) for _ in range(GROUP_SIZE)]
        for api in apis:
            api.post("/api/matching/join/")
        bodies = [api.get("/api/matching/status/").json() for api in apis]
        self.assertTrue(all(b["status"] == State.MATCHED for b in bodies))
        self.assertEqual(len({b["room"]["room_name"] for b in bodies}), 1)

        self.assertEqual(apis[0].post("/api/matching/join/").status_code, 409)
        res = apis[0].post("/api/matching/call/enter/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], State.IN_CALL)
        res = apis[0].post("/api/matching/call/leave/")
        self.assertEqual(res.json()["status"], State.NONE)
        self.assertNotIn("room", res.json())

    def test_room_not_exposed_to_others(self) -> None:
        apis = [self.client_for(new_guest()[0]) for _ in range(GROUP_SIZE)]
        for api in apis:
            api.post("/api/matching/join/")
        outsider = self.client_for(new_guest()[0])
        body = outsider.get("/api/matching/status/").json()
        self.assertNotIn("room", body)
        self.assertEqual(outsider.post("/api/matching/call/enter/").status_code, 404)

    def test_enter_after_expiry(self) -> None:
        apis = [self.client_for(new_guest()[0]) for _ in range(GROUP_SIZE)]
        for api in apis:
            api.post("/api/matching/join/")
        expire_room(Room.objects.get())
        # enter の先頭の遅延評価でグループが終了するため、所属なし(404)になる。410の経路はサービス層のテストで確認する
        res = apis[0].post("/api/matching/call/enter/")
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()["status"], State.NONE)

    def test_status_expires_timed_out_waiting(self) -> None:
        client_id, user = new_guest()
        api = self.client_for(client_id)
        api.post("/api/matching/join/")
        WaitingQueue.objects.filter(user=user).update(created_at=timezone.now() - QUEUE_TIMEOUT)
        self.assertEqual(api.get("/api/matching/status/").json()["status"], State.NONE)

    def test_cors_allows_client_id_header(self) -> None:
        res = self.api.options(
            "/api/matching/status/",
            HTTP_ORIGIN="http://localhost:8081",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="x-client-id",
        )
        self.assertEqual(res.headers.get("Access-Control-Allow-Origin"), "http://localhost:8081")
        self.assertIn("x-client-id", res.headers.get("Access-Control-Allow-Headers", ""))
