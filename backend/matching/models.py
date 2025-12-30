from django.db import models

from accounts.models import CustomUser


class WaitingQueue(models.Model):
    user = models.ForeignKey(CustomUser, related_name="waiting", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True, db_comment="作成日時")


class Room(models.Model):
    users = models.ManyToManyField(CustomUser, related_name="rooms", default=[])
    created_at = models.DateTimeField(auto_now_add=True, null=True, db_comment="作成日時")
