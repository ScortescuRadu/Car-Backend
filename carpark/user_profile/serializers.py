from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'car_id']


class UserProfileCreateSerializer(serializers.ModelSerializer):
    token = serializers.CharField()

    class Meta:
        model = UserProfile
        fields = ['token', 'username', 'car_id']


class UserProfileTokenSerializer(serializers.Serializer):
    token = serializers.CharField()