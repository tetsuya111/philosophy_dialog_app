from django.urls import path
from .views import MoveUserToChatView

urlpatterns = [
    # Example usage: POST /startchat/2/ (where 2 is the status code)
    path('startchat/<int:new_status_code>/', MoveUserToChatView.as_view(), name='start_chat'),
]