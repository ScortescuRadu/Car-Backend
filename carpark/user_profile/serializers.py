from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'car_id']


class UserProfileTokenSerializer(serializers.Serializer):
    token = serializers.CharField()