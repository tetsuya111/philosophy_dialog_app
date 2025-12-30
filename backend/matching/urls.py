from django.urls import path

from .views import join_matching

urlpatterns = [
    path("join/", join_matching),
    path("status/"),
    path("cancel/"),
]
