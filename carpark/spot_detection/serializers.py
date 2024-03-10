from rest_framework import serializers
from .models import BoundingBox

class BoundingBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoundingBox
        fields = ['task_id', 'bounding_boxes_json']

class ImageProcessSerializer(serializers.Serializer):
    image = serializers.ImageField()

    def create(self, validated_data):
        # This method is not used since we override the create logic in the view
        pass