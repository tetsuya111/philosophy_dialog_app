"""WebRTC app URL configuration."""

from django.urls import path

from . import views

urlpatterns = [
    path("rooms/", views.list_rooms, name="list_rooms"),
    path("rooms/create/", views.create_room, name="create_room"),
    path("rooms/<str:room_id>/", views.get_room, name="get_room"),
    path("rooms/<str:room_id>/join/", views.join_room, name="join_room"),
]
