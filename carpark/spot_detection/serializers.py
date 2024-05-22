from rest_framework import serializers
from .models import BoundingBox
from parking_spot.models import ParkingSpot

class BoundingBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoundingBox
        fields = ['task_id', 'bounding_boxes_json']

class ImageProcessSerializer(serializers.Serializer):
    image = serializers.ImageField()

    def create(self, validated_data):
        # This method is not used since we override the create logic in the view
        pass

class BoundingBoxInputSerializer(serializers.Serializer):
    token = serializers.CharField()
    street_address = serializers.CharField()
    camera_address = serializers.CharField()
    bounding_boxes = serializers.ListField(child=serializers.JSONField())

    class Meta:
        fields = ['token', 'street_address', 'camera_address', 'bounding_boxes']