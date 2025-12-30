from collections.abc import Callable
from typing import cast

from rest_framework.request import Request
from rest_framework.response import Response

ACCESS_TOKEN_COOKIE_NAME: str = "POST_PROCESSING_ACCESS_TOKEN"


class AuthorizationHeaderMiddleware:
    def __init__(self, get_response: Callable[[Request], Response] | None = None) -> None:
        get_response = cast("Callable[[Request], Response]", get_response)
        self.get_response = get_response

    def __call__(self, request: Request) -> Response:
        if request.path not in ["/api/auth/login/", "/swagger/"]:
            access_token = request.COOKIES.get(ACCESS_TOKEN_COOKIE_NAME)
            request.META["HTTP_AUTHORIZATION"] = f"JWT {access_token}"
        return self.get_response(request)
