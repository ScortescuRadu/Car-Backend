from rest_framework import serializers
from .models import ParkingInvoice
from django.utils import timezone
from decimal import Decimal, getcontext
from parking_lot.models import ParkingLot

class ParkingInvoiceSerializer(serializers.ModelSerializer):
    address = serializers.CharField(source='parking_lot.address', read_only=True)  # Add this line

    class Meta:
        model = ParkingInvoice
        fields = ['parking_lot', 'hourly_price', 'spot_description',
        'timestamp', 'time_spent', 'final_cost', 'license_plate', 'address']


class ParkingInvoiceReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingInvoice
        fields = [ 'user', 'parking_lot', 'timestamp', 'hourly_price', 'spot_description',
                  'is_paid', 'final_cost', 'license_plate', 'reserved_time']

    def create(self, validated_data):
        validated_data['timestamp'] = timezone.now()
        validated_data['spot_description'] = "Default spot"
        return super().create(validated_data)


class LicensePlateSerializer(serializers.Serializer):
    license_plate = serializers.CharField(max_length=255)


class ParkingInvoiceOutputSerializer(serializers.ModelSerializer):
    final_cost = serializers.SerializerMethodField()
    time_spent = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()

    class Meta:
        model = ParkingInvoice
        fields = ['timestamp', 'hourly_price', 'spot_description', 'final_cost', 'time_spent', 'address']

    def get_final_cost(self, obj):
        # Calculate the difference in hours between the current time and the timestamp
        time_difference = timezone.now() - obj.timestamp
        hours_spent = time_difference.total_seconds() / 3600
        # Convert hours_spent to Decimal, round it and ensure a minimum of 1 hour
        hours_spent_decimal = Decimal(max(round(hours_spent), 1))
        # Calculate the final cost
        final_cost = obj.hourly_price * hours_spent_decimal
        # Return the result rounded to 2 decimal places
        return final_cost.quantize(Decimal('0.01'))  # This uses the quantize method to round to two decimal places

    def get_address(self, obj):
        # Fetch the parking lot address using the parking_lot_id
        try:
            return parking_lot.street_address
        except ParkingLot.DoesNotExist:
            return "Address not found"

    def get_time_spent(self, obj):
        # Calculate the time spent in hours
        time_difference = timezone.now() - obj.timestamp
        hours_spent = time_difference.total_seconds() / 3600
        # Round the hours and ensure a minimum of 1 hour
        return max(round(hours_spent), 1)


class PriceCalculationInputSerializer(serializers.Serializer):
    license_plate = serializers.CharField(max_length=255)
    timestamp = serializers.DateTimeField()

    def validate_timestamp(self, value):
        """Ensure the timestamp is in the past."""
        if value > timezone.now():
            raise serializers.ValidationError("Timestamp cannot be in the future.")
        return value

class PriceOutputSerializer(serializers.Serializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
