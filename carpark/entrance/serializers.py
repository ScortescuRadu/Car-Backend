from rest_framework import serializers
from .models import Entrance

class EntranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entrance
        fields = ['latitude', 'longitude']