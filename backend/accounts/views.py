from typing import TYPE_CHECKING, ClassVar, cast

from django.conf import settings
from django.contrib.auth.hashers import make_password
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.middleware import ACCESS_TOKEN_COOKIE_NAME

from .models import CustomUser
from .serializers import CustomUserSerializer, MyTokenObtainPairSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request


class LoginView(APIView):
    """ユーザーのログイン処理

    Args:
        APIView (class): rest_framework.viewsのAPIViewを受け取る
    """

    serializer_class = MyTokenObtainPairSerializer

    # アクセス許可の指定
    authentication_classes: ClassVar[list] = []
    permission_classes: ClassVar[list] = []

    @swagger_auto_schema(
        request_body=MyTokenObtainPairSerializer,
        responses={
            status.HTTP_200_OK: "",
            status.HTTP_400_BAD_REQUEST: "raise_exception",
            status.HTTP_401_UNAUTHORIZED: '{"errMsg": "ユーザーの認証に失敗しました"}',
        },
    )
    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        print("XXX", request.data)
        serializer.is_valid(raise_exception=True)
        print("XXX")
        validated_data = cast("dict", serializer.validated_data)
        print("XXX")
        access = validated_data.get("access")
        print("XXX")

        if access:
            response = Response(status=status.HTTP_200_OK)
            max_age = settings.COOKIE_TIME
            response.set_cookie(
                ACCESS_TOKEN_COOKIE_NAME,
                access,
                httponly=True,
                max_age=max_age,
            )

            return response
        return Response(
            {"errMsg": "ユーザーの認証に失敗しました"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class UserView(APIView):
    """ユーザーの処理

    Args:
        APIView (class): rest_framework.viewsのAPIViewを受け取る
    """

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get(self, request: Request) -> Response:
        username = request.user.username
        data = {
            "userid": request.user.pk,
            "username": username,
            "matching_status": request.user.matching_status,
        }
        return Response(data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """ユーザーのログアウト処理

    Args:
        APIgView (class): rest_framework.viewsのAPIViewを受け取る
    """

    @swagger_auto_schema(responses={status.HTTP_200_OK: ""})
    def get(self, _: Request) -> Response:
        response = Response(status=status.HTTP_200_OK)
        response.delete_cookie(ACCESS_TOKEN_COOKIE_NAME)
        return response


class RegisterView(generics.CreateAPIView):
    """ユーザー登録用ビュー"""

    # アクセス許可の指定
    authentication_classes: ClassVar[list] = []
    permission_classes: ClassVar[list] = []

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def create(self, request: Request) -> Response:
        password = make_password(request.data["password"])
        request.data["password"] = password
        return super().create(request)


class DestroyView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def destroy(self, request: Request) -> Response:
        self.kwargs = {
            **self.kwargs,
            "pk": request.user.pk,
        }
        return super().destroy(request)
