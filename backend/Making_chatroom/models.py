from django.db import models
from accounts.models import CustomUser


class ChatRoom(models.Model):
    # Standard auto-incrementing ID is created automatically as 'id' (ChatroomID)
    created_at = models.DateTimeField(auto_now_add=True)
    # ManyToMany allows any number of users to be in this chat
    users = models.ManyToManyField(CustomUser, related_name='active_chats')

    def __str__(self):
        return f"ChatRoom {self.id}"
    
class Room(models.Model):
    users = models.ManyToManyField(CustomUser, related_name="rooms")
    created_at = models.DateTimeField(auto_now_add=True, null=True, db_comment="作成日時")
    active_chat_room = models.ForeignKey(ChatRoom, on_delete=models.SET_NULL, null=True, blank=True, related_name="active_chat_room")
