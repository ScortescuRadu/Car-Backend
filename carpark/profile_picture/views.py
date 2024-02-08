from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ProfilePicture
from .serializers import ProfilePictureSerializer

# Create your views here.

class UserProfilePictureUpload(generics.CreateAPIView):
    serializer_class = ProfilePictureSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        # Check if a profile picture already exists for the user
        user = request.user
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
        serializer.save(user=self.request.user)


class UserProfilePictureRetrieve(generics.RetrieveAPIView):
    queryset = ProfilePicture.objects.all()
    serializer_class = ProfilePictureSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        # Retrieve the profile picture for the current user
        user = self.request.user
        obj, created = ProfilePicture.objects.get_or_create(user=user)
        return obj