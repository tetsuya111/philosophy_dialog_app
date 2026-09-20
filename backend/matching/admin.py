from typing import ClassVar

from django.contrib import admin

from .models import GuestClient, Room, RoomMember, WaitingQueue


class RoomMemberInline(admin.TabularInline):
    model = RoomMember
    extra = 0


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "end_reason", "created_at", "expires_at", "ended_at")
    inlines: ClassVar = [RoomMemberInline]


@admin.register(WaitingQueue)
class WaitingQueueAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")


@admin.register(GuestClient)
class GuestClientAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")
    exclude = ("client_id_hash",)
