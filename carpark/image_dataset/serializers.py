from rest_framework import serializers
from .models import ImageDataset

class ImageDatasetSerializer(serializers.ModelSerializer):
    street_address = serializers.CharField(write_only=True)
    bounding_boxes = serializers.JSONField(write_only=True)

    class Meta:
        model = ImageDataset
        fields = ['id', 'street_address', 'image', 'bounding_boxes', 'original_image_width', 'original_image_height']

class ImageDatasetRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageDataset
        fields = ['id', 'parking_lot', 'image', 'bounding_boxes_json', 'original_image_width', 'original_image_height']