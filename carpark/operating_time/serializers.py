from rest_framework import serializers
from .models import OperatingHours

class OperatingHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperatingHours
        fields = ['day', 'opening_time', 'closing_time']