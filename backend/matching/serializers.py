
from rest_framework import serializers

from .models import UserMatchingStatus


class UserMatchingStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserMatchingStatus
        fields = "__all__"
