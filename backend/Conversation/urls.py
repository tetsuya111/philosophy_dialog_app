from django.urls import path
from .views import UserChatHistoryView, SendMessageView

urlpatterns = [
    path('my-conversations/', UserChatHistoryView.as_view(), name='chat_history'),
    path('chat/<int:room_id>/send/', SendMessageView.as_view(), name='send_message'),
]