from rest_framework import serializers
from .models import ParkEntrance

class ParkEntranceSerializer(serializers.ModelSerializer):
    camera_address = serializers.CharField(source='image_task.camera_address', read_only=True)

    class Meta:
        model = ParkEntrance
        fields = ['id', 'license_plate', 'timestamp', 'camera_address']
