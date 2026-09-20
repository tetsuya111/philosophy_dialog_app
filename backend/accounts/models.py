from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models


class CustomUserManager(UserManager):
    pass


# Create your models here.
class CustomUser(AbstractBaseUser):
    username = models.CharField(max_length=40, unique=True, db_comment="ユーザー名")
    created_at = models.DateTimeField(auto_now_add=True, null=True, db_comment="作成日時")
    updated_at = models.DateTimeField(auto_now=True, null=True, db_comment="更新日時")
    USERNAME_FIELD = "username"
    objects = CustomUserManager()

    class Meta:
        db_table = "custom_user"
        db_table_comment = "カスタムユーザー"
