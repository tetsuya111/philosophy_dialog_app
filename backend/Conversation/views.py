from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Message, ChatRoom
from .serializers import MessageSerializer

class UserChatHistoryView(APIView): # Renamed to match URLs
    permission_classes = [IsAuthenticated] # Added Security

    def get(self, request):
        # STEP 1: Get IDs
        chatroom_ids = list(
            ChatRoom.objects
            .filter(users=request.user)
            .values_list("id", flat=True)
        )

        if not chatroom_ids:
            return Response([])

        # STEP 2: Get messages
        messages_qs = (
            Message.objects
            .filter(conversation_id__in=chatroom_ids)
            .order_by("timestamp") # Usually sorting by time is enough
        )

        serializer = MessageSerializer(messages_qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        # 1. Check room exists and user is inside it
        room = get_object_or_404(ChatRoom, id=room_id, users=request.user)

        # 2. Serialize
        serializer = MessageSerializer(data=request.data)
        
        # 3. Validate (Now works because sender/conversation are read_only)
        if serializer.is_valid():
            serializer.save(sender=request.user, conversation=room)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)