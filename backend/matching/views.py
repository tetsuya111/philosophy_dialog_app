from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from django.db import OperationalError
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from . import services
from .authentication import ClientIdAuthentication
from .serializers import serialize_state

if TYPE_CHECKING:
    from rest_framework.request import Request


class MatchingAPIView(APIView):
    """ランダムコールのAPIの基底クラス。ログインなしで、X-Client-Id の利用者識別子で認証する。"""

    authentication_classes: ClassVar = [ClientIdAuthentication]
    permission_classes: ClassVar = [IsAuthenticated]

    def handle_exception(self, exc: Exception) -> Response:
        if isinstance(exc, OperationalError):
            # SQLiteの書き込みロック競合(database is locked)。クライアントは次のポーリング・再操作で回復する
            return Response({"detail": "混み合っています。しばらくしてから再度お試しください"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return super().handle_exception(exc)

    def state_response(self, request: Request, http_status: int = status.HTTP_200_OK, detail: str | None = None) -> Response:
        data: dict[str, Any] = serialize_state(services.get_state(request.user))
        if detail is not None:
            data["detail"] = detail
        return Response(data, status=http_status)


class ClientView(APIView):
    """利用者識別子を発行する。認証不要。ゲストユーザーの大量作成を防ぐためレート制限をかける。"""

    authentication_classes: ClassVar = []
    permission_classes: ClassVar = [AllowAny]
    throttle_classes: ClassVar = [ScopedRateThrottle]
    throttle_scope = "matching_client"

    def post(self, request: Request) -> Response:  # noqa: ARG002
        return Response({"client_id": services.issue_client()}, status=status.HTTP_201_CREATED)


class StatusView(MatchingAPIView):
    def get(self, request: Request) -> Response:
        services.expire_stale()
        return self.state_response(request)


class JoinView(MatchingAPIView):
    def post(self, request: Request) -> Response:
        services.expire_stale()
        try:
            services.join_queue(request.user)
        except services.AlreadyInRoomError:
            return self.state_response(request, status.HTTP_409_CONFLICT, "マッチング済みまたは通話中のため待機列に参加できません")
        return self.state_response(request)


class CancelView(MatchingAPIView):
    def post(self, request: Request) -> Response:
        try:
            services.cancel_queue(request.user)
        except services.NotWaitingError:
            return self.state_response(request, status.HTTP_409_CONFLICT, "待機中ではありません")
        return self.state_response(request)


class EnterCallView(MatchingAPIView):
    def post(self, request: Request) -> Response:
        services.expire_stale()
        try:
            services.enter_call(request.user)
        except services.NotInRoomError:
            return self.state_response(request, status.HTTP_404_NOT_FOUND, "参加中のグループがありません")
        except services.RoomEndedError:
            return self.state_response(request, status.HTTP_410_GONE, "通話の有効時間が終了しました")
        return self.state_response(request)


class LeaveCallView(MatchingAPIView):
    def post(self, request: Request) -> Response:
        services.leave_call(request.user)
        return self.state_response(request)
