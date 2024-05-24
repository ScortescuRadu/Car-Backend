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
        fields = ['street_address', 'camera_address', 'camera_type', 'device_id', 'label']