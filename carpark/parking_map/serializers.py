from rest_framework import serializers
from .models import ParkingLotTile

class ParkingLotTileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingLotTile
        fields = ['id', 'parking_lot', 'tiles_data']
