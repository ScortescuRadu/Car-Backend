from rest_framework import serializers
from .models import ParkingLot
from ocupancy_metrics.models import OccupancyMetrics

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


class CityNameSerializer(serializers.Serializer):
    city_name = serializers.CharField(max_length=255)


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


class UserParkAddressInputSerializer(serializers.Serializer):
    token = serializers.CharField()
    street_address = serializers.CharField()


class ParkPriceUpdateSerializer(serializers.Serializer):
    price = serializers.CharField()


class ParkPhoneUpdateSerializer(serializers.Serializer):
    phone = serializers.CharField()


class ParkTimesUpdateSerializer(serializers.Serializer):
    weekdayOpening = serializers.TimeField(allow_null=True)
    weekdayClosing = serializers.TimeField(allow_null=True)
    weekendOpening = serializers.TimeField(allow_null=True)
    weekendClosing = serializers.TimeField(allow_null=True)


class ParkCapacityUpdateSerializer(serializers.Serializer):
    capacity = serializers.IntegerField()


class ParkAddressUpdateSerializer(serializers.Serializer):
    new_address = serializers.IntegerField()
    new_latitude = serializers.IntegerField()
    new_longitude = serializers.IntegerField()


class ParkingLotRadiusSearchSerializer(serializers.ModelSerializer):
    current_occupancy = serializers.SerializerMethodField()

    class Meta:
        model = ParkingLot
        fields = ['id', 'price', 'capacity', 'street_address', 'latitude', 'longitude', 'current_occupancy']

    def get_current_occupancy(self, obj):
        occupancy_metrics = OccupancyMetrics.objects.filter(parking_lot=obj).first()
        if occupancy_metrics:
            return occupancy_metrics.total_current_occupancy
        return None