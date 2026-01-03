from django.urls import path

from .views import cancel_matching, join_matching

urlpatterns = [
    path("join/", join_matching),
    path("cancel/", cancel_matching),
]
