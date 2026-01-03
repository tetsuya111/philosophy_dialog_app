from rest_framework import serializers
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    # Optional: Display username instead of just User ID
    sender_username = serializers.ReadOnlyField(source='sender.username')

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'sender_username', 'content', 'timestamp']
        # CRITICAL FIX: Tell Django these fields are NOT required from the user
        read_only_fields = ['sender', 'conversation']