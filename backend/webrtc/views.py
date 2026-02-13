"""WebRTC room management API views."""

import secrets
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["POST"])
def create_room(request):
    """Create a new WebRTC room (mock implementation)."""
    room_id = secrets.token_urlsafe(16)
    return Response(
        {
            "room_id": room_id,
            "room_name": f"Room-{room_id[:8]}",
            "jitsi_domain": "meet.jit.si",
            "max_participants": 4,
            "created_at": "2026-02-12T00:00:00Z",
        }
    )


@api_view(["GET"])
def get_room(request, room_id):
    """Get room information (mock implementation)."""
    return Response(
        {
            "room_id": room_id,
            "room_name": f"Room-{room_id[:8]}",
            "jitsi_domain": "meet.jit.si",
            "participants_count": 1,
            "max_participants": 4,
            "is_active": True,
        }
    )


@api_view(["GET"])
def list_rooms(request):
    """List all available rooms (mock implementation)."""
    return Response(
        {
            "rooms": [
                {
                    "room_id": "mock_room_1",
                    "room_name": "Room-mock_roo",
                    "participants_count": 2,
                    "max_participants": 4,
                    "is_active": True,
                },
                {
                    "room_id": "mock_room_2",
                    "room_name": "Room-mock_roo",
                    "participants_count": 1,
                    "max_participants": 4,
                    "is_active": True,
                },
            ]
        }
    )


@api_view(["POST"])
def join_room(request, room_id):
    """Join a room (mock implementation)."""
    return Response(
        {
            "success": True,
            "room_id": room_id,
            "jitsi_domain": "meet.jit.si",
            "room_name": f"Room-{room_id[:8]}",
            "jwt_token": None,  # For future JWT implementation
        }
    )
