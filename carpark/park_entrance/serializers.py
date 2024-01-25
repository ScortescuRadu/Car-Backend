from rest_framework import serializers
from .models import ParkingEntrance

class ParkEntranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingEntrance
        fields = ['parking_lot', 'entrance']