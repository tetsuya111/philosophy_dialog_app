from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import GuestClient

if TYPE_CHECKING:
    from rest_framework.request import Request

    from accounts.models import CustomUser

CLIENT_ID_HEADER: str = "HTTP_X_CLIENT_ID"


def hash_client_id(client_id: str) -> str:
    """利用者識別子をDB保存・照合用にハッシュ化する(平文は保存しない)。"""
    return hashlib.sha256(client_id.encode()).hexdigest()


class ClientIdAuthentication(BaseAuthentication):
    """ログインなしの利用者を X-Client-Id ヘッダーの利用者識別子で認証する。"""

    def authenticate(self, request: Request) -> tuple[CustomUser, None] | None:
        client_id = request.META.get(CLIENT_ID_HEADER)
        if not client_id:
            return None
        guest = GuestClient.objects.select_related("user").filter(client_id_hash=hash_client_id(client_id)).first()
        if guest is None:
            msg = "利用者識別子が不正です"
            raise AuthenticationFailed(msg)
        return guest.user, None

    def authenticate_header(self, request: Request) -> str:  # noqa: ARG002
        # 401(未認証)を返すために必要。未実装だとDRFは403を返す
        return "ClientId"
