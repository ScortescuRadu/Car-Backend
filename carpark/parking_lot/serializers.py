from rest_framework import serializers
from .models import ParkingLot

class ParkingLotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingLot
        fields = ['price', 'capacity']


class UserParkingLotSerializer(serializers.ModelSerializer):
    token = serializers.CharField(write_only=True)

    class Meta:
        model = ParkingLot
        fields = ['token', 'price', 'capacity']

    def create(self, validated_data):
        # Extract the token from validated data and remove it
        token = validated_data.pop('token', None)

        user_id = Token.objects.get(key=token).user_id
        user = User.objects.get(id=user_id)

        if not user:
            raise serializers.ValidationError('Invalid token')

        # Create a new ParkingLot instance
        parking_lot = ParkingLot.objects.create(**validated_data)

        # Your logic to create a UserPark entry
        create_user_park_entry(user, parking_lot)

        return parking_lot


class UserParkInputSerializer(serializers.Serializer):
    token = serializers.CharField()

class UserParkOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingLot
        fields = '__all__'