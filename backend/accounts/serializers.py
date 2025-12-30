from typing import Self, cast

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.models import TokenUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token

from .models import CustomUser


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWSのペイロードにusernameを追加する"""

    @classmethod
    def get_token(cls: type[Self], user: TokenUser | AbstractBaseUser) -> Token:
        user = cast("User", user)
        token = super().get_token(user)
        token["username"] = user.username
        return token


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"
