from rest_framework import serializers
from .models import ParkingLot, ParkingSpot

class ParkingSpotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSpot
        fields = ['id', 'level', 'sector', 'number', 'is_occupied']


class ParkingSpotInputSerializer(serializers.Serializer):
    token = serializers.CharField()
    street_address = serializers.CharField()

    class Meta:
        model = ParkingSpot
        fields = ['token', 'street_address', 'level', 'sector', 'number', 'is_occupied']


class SpotByAddressInputSerializer(serializers.Serializer):
    street_address = serializers.CharField()

    class Meta:
        model = ParkingLot
        fields = ['street_address']