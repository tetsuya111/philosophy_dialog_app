from django.db import models

from accounts.models import CustomUser

from .choices import UserMatchingStatus


# Create your models here.
class UserMatchingStatus(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="matching_status", db_comment="ユーザー")
    status = models.IntegerField(choices=UserMatchingStatus, db_comment="状態")


class Room(models.Model):
    users = models.ManyToManyField(CustomUser, related_name="rooms")
    created_at = models.DateTimeField(auto_now_add=True, null=True, db_comment="作成日時")
