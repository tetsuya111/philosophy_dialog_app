from django.db import models
from accounts.models import CustomUser
from Making_chatroom.models import ChatRoom

class Message(models.Model):
    # Fixed related_name to 'messages'
    conversation = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}..."