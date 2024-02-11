from rest_framework import serializers
from .models import ParkingInvoice

class ParkingInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingInvoice
        fields = ['parking_lot_id', 'hourly_price', 'spot_description',
        'timestamp', 'time_spent', 'final_cost']