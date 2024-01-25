from rest_framework import serializers
from .models import UserPark

class UserParkSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPark
        fields = ['user', 'parking_lot']