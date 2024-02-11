from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ProfilePicture
from .serializers import ProfilePictureSerializer
from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

# Create your views here.

class UserProfilePictureUpload(generics.CreateAPIView):
    serializer_class = ProfilePictureSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsAuthenticated,)
    authentication_classes = [TokenAuthentication]

    def get_user_from_token(self, request):
        # Extract user from the authentication token
        user, _ = TokenAuthentication().authenticate(request)
        return user

    def create(self, request, *args, **kwargs):
        # Check if a profile picture already exists for the user
        user = self.get_user_from_token(request)
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


class UserProfilePictureRetrieve(generics.RetrieveAPIView):
    queryset = ProfilePicture.objects.all()
    serializer_class = ProfilePictureSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = [TokenAuthentication]

    def get_user_from_token(self, request):
        # Extract user from the authentication token
        user, _ = TokenAuthentication().authenticate(request)
        return user

    def get_object(self, *args, **kwargs):
        # Retrieve the profile picture for the current user
        user = self.get_user_from_token(self.request)
        obj, created = ProfilePicture.objects.get_or_create(user=user)
        return obj