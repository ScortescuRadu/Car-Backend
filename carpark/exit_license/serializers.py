from rest_framework import serializers
from .models import ParkingExit

class ParkingExitSerializer(serializers.ModelSerializer):
    camera_address = serializers.CharField(source='image_task.camera_address', read_only=True)

    class Meta:
        model = ParkingExit
        fields = ['id', 'license_plate', 'timestamp', 'is_paid', 'camera_address']
