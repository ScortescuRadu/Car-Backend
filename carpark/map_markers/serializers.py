from rest_framework import serializers
from .models import Marker, Subscription

class MarkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marker
        fields = ['latitude', 'longitude', 'timestamp']

# For retrieving the list of markers
class MarkersListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marker
        fields = ['latitude', 'longitude', 'is_subscribed']
    def get_is_subscribed(self, obj):
        return Subscription.objects.filter(marker=obj).exists()

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['user', 'marker']