from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.utils import timezone

from .constants import QUEUE_TIMEOUT
from .services import State

if TYPE_CHECKING:
    from .services import UserState


def serialize_state(state: UserState) -> dict[str, Any]:
    """ユーザーの状態をAPIレスポンスの形式にする。

    server_time はクライアントが端末時刻とのずれを補正して残り時間を表示するために返す。
    room_name は本人の状態としてのみ返す。
    """
    data: dict[str, Any] = {"status": state.status, "server_time": timezone.now().isoformat()}
    if state.status == State.WAITING and state.waiting is not None:
        data["waiting"] = {
            "since": state.waiting.created_at.isoformat(),
            "expires_at": (state.waiting.created_at + QUEUE_TIMEOUT).isoformat(),
        }
    if state.status in (State.MATCHED, State.IN_CALL) and state.room is not None:
        data["room"] = {
            "room_name": state.room.room_name,
            "expires_at": state.room.expires_at.isoformat(),
        }
    return data
