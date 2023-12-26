from rest_framework import serializers
from .models import Marker

class MarkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marker
        fields = ['latitude', 'longitude', 'timestamp']

class MarkersListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marker
        fields = ['latitude', 'longitude']