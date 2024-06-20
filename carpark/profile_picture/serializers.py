from rest_framework import serializers
from .models import ProfilePicture
from rest_framework.authentication import TokenAuthentication

class ProfilePictureSerializer(serializers.ModelSerializer):
    token = serializers.CharField(write_only=True)

    class Meta:
        model = ProfilePicture
        fields = ['cover', 'token']

    def create(self, validated_data):
        token = validated_data.pop('token')
        request = self.context.get('request')
        
        # Authenticate the user using the token
        request.META['HTTP_AUTHORIZATION'] = f'Token {token}'
        user, _ = TokenAuthentication().authenticate(request)

        # Ensure 'user' is not in validated_data to avoid conflict
        validated_data['user'] = user
        
        # Create the ProfilePicture instance with the authenticated user
        profile_picture = ProfilePicture.objects.create(**validated_data)
        return profile_picture


class ProfilePictureTokenSerializer(serializers.Serializer):
    token = serializers.CharField()