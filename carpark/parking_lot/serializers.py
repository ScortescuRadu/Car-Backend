from rest_framework import serializers
from .models import ParkingLot

class ParkingLotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingLot
        fields = ['price', 'capacity', 'iban', 'phone_number', 'weekday_opening_time',
        'weekday_closing_time', 'weekend_opening_time', 'weekend_closing_time', 'street_address']

class TestParkingLotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingLot
        fields = '__all__'

class StreetAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingLot
        fields = ['street_address']

class UserParkingLotSerializer(serializers.ModelSerializer):
    token = serializers.CharField(write_only=True)

    class Meta:
        model = ParkingLot
        fields = ['token', 'price', 'capacity', 'iban', 'phone_number', 'weekday_opening_time',
        'weekday_closing_time', 'weekend_opening_time', 'weekend_closing_time', 'street_address']

    def create(self, validated_data):
        token = validated_data.pop('token', None)

        user_id = Token.objects.get(key=token).user_id
        user = User.objects.get(id=user_id)

        if not user:
            raise serializers.ValidationError('Invalid token')

        parking_lot = ParkingLot.objects.create(**validated_data)

        create_user_park_entry(user, parking_lot)

        return parking_lot


class UserParkInputSerializer(serializers.Serializer):
    token = serializers.CharField()

class UserParkOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingLot
        fields = '__all__'