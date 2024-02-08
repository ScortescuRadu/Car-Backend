from rest_framework import serializers
from .models import ProfilePicture

class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfilePicture
        fields = ['cover']

    def save(self, user, **kwargs):
        # Associate the user with the profile picture
        return super().save(user=user, **kwargs)