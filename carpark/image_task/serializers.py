from rest_framework import serializers
from .models import ImageTask

class ImageTaskUserInputSerializer(serializers.ModelSerializer):
    token = serializers.CharField()
    class Meta:
        model = ImageTask
        fields = ['camera_type', 'token']


class ImageTaskUserOutputSerializer(serializers.ModelSerializer):
    street_address = serializers.CharField(source='parking_lot.street_address')

    class Meta:
        model = ImageTask
        fields = ['street_address', 'camera_address', 'camera_type', 'device_id', 'label', 'destination_type']


class FrameInputSerializer(serializers.Serializer):
    image_0 = serializers.ImageField()
    device_id_0 = serializers.CharField()
    parking_lot = serializers.CharField()
    token = serializers.CharField(required=False, allow_blank=True)


class DetectionSerializer(serializers.Serializer):
    xmin = serializers.FloatField()
    ymin = serializers.FloatField()
    xmax = serializers.FloatField()
    ymax = serializers.FloatField()
    confidence = serializers.FloatField()
    class_name = serializers.CharField()


class FrameOutputSerializer(serializers.Serializer):
    camera_address = serializers.CharField()
    parking_lot = serializers.CharField()
    detections = DetectionSerializer(many=True)


class DetectionOCRSerializer(serializers.Serializer):
    xmin = serializers.FloatField()
    ymin = serializers.FloatField()
    xmax = serializers.FloatField()
    ymax = serializers.FloatField()
    confidence = serializers.FloatField()
    class_name = serializers.CharField()
    ocr_text = serializers.CharField(required=False, allow_blank=True)  # New field for OCR result


class FrameOutputOCRSerializer(serializers.Serializer):
    camera_address = serializers.CharField()
    parking_lot = serializers.CharField()
    detections = DetectionOCRSerializer(many=True)