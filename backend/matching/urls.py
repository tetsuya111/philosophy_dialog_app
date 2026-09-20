from django.urls import path

from .views import CancelView, ClientView, EnterCallView, JoinView, LeaveCallView, StatusView

urlpatterns = [
    path("client/", ClientView.as_view()),
    path("status/", StatusView.as_view()),
    path("join/", JoinView.as_view()),
    path("cancel/", CancelView.as_view()),
    path("call/enter/", EnterCallView.as_view()),
    path("call/leave/", LeaveCallView.as_view()),
]
