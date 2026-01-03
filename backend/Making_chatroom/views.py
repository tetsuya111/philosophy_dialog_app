from django.db import transaction
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status  # This module is safe now

# Assuming these imports exist in your project
from matching.models import UserMatchingStatus 
# from matching.serializers import UserMatchingStatusSerializer # Not strictly needed if we don't use it for validation here
from .models import ChatRoom, Room

class MoveUserToChatView(APIView):

    # Renamed 'status' to 'new_status_code' to avoid conflict with the imported 'status' module
    def post(self, request: Request, new_status_code: int) -> Response:
        
        # Validation: Ensure the integer passed is a valid status option
        # Note: If UserMatchingStatus is a TextChoices/IntegerChoices, use .values
        if new_status_code not in UserMatchingStatus.values:
            return Response(
                {"error": "Invalid status code"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                # 1. Lock the room so no one else modifies it while we work
                # Note: This assumes a user is only ever in ONE Room at a time.
                room = Room.objects.select_for_update().get(users=request.user)

                # 2. Update User Status
                request.user.matching_status = new_status_code
                request.user.save()  # FIX: Save the user instance, not the class

                # 3. Check if a ChatRoom already exists for this Room
                chat_room = room.active_chat_room

                if not chat_room:
                    # 4. Create ChatroomID if not created
                    chat_room = ChatRoom.objects.create()
                    room.active_chat_room = chat_room
                    room.save()

                # 5. Delete userID from RoomModel (Remove from waiting list)
                room.users.remove(request.user)

                # 6. Add userID to ChatRoom table
                chat_room.users.add(request.user)

                # 7. Return ChatroomID to frontend
                return Response({
                    "message": "User moved to chat successfully",
                    "chatroom_id": chat_room.id,
                    "user_status": "disconnected" # Or whatever logic matches new_status_code
                }, status=status.HTTP_200_OK)

        except Room.DoesNotExist:
            return Response(
                {"error": "User is not currently in any Room"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )