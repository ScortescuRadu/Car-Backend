from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ProfilePicture
from .serializers import ProfilePictureSerializer, ProfilePictureTokenSerializer
from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.exceptions import ValidationError

# Create your views here.

class UserProfilePictureUpload(generics.CreateAPIView):
    serializer_class = ProfilePictureSerializer
    parser_classes = (MultiPartParser, FormParser)
    authentication_classes = [TokenAuthentication]

    def get_user_from_token(self, request):
        # Extract user from the authentication token
        user, _ = TokenAuthentication().authenticate(request)
        return user

    def create(self, request, *args, **kwargs):
        # Extract the token from the request data
        token = request.data.get('token')
        if not token:
            raise ValidationError("Token is required.")

        # Create a mock request with the token in the headers for authentication
        request.META['HTTP_AUTHORIZATION'] = f'Token {token}'
        user = self.get_user_from_token(request)
        
        # Check if a profile picture already exists for the user
        existing_picture = ProfilePicture.objects.filter(user=user).first()

        # If there's an existing picture, delete it
        if existing_picture:
            existing_picture.cover.delete()  # Delete old picture
            existing_picture.cover = request.data.get('cover')
            existing_picture.save()
        else:
            return super().create(request, *args, **kwargs)

        return Response({'message': 'Profile picture updated successfully.'}, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        # Associate the user with the profile picture
        serializer.save(user=self.get_user_from_token(self.request))


class UserProfilePictureRetrieve(generics.GenericAPIView):
    serializer_class = ProfilePictureTokenSerializer
    authentication_classes = [TokenAuthentication]

    def get_user_from_token(self, token):
        request = self.request
        request.META['HTTP_AUTHORIZATION'] = f'Token {token}'
        user, _ = TokenAuthentication().authenticate(request)
        return user

    def post(self, request, *args, **kwargs):
        # Validate the input serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract the token from the validated data
        token = serializer.validated_data['token']
        user = self.get_user_from_token(token)
        
        # Retrieve the profile picture for the authenticated user
        profile_picture = ProfilePicture.objects.filter(user=user).first()
        
        if not profile_picture or not profile_picture.cover:
            return Response({'detail': 'Profile picture not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Get the URL of the profile picture
        image_url = profile_picture.cover.url

        return Response({'cover': image_url}, status=status.HTTP_200_OK)