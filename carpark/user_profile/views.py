from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import UserProfile
from .serializers import UserProfileSerializer
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

# Create your views here.

class UserProfileCreateView(generics.CreateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        username = serializer.validated_data['username']

        if UserProfile.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists.'}, status=400)
        
         # Check if a UserProfile with the provided username already exists for the user
        existing_profile = UserProfile.objects.filter(user=self.request.user.id).first()

        if existing_profile:
            # Update the existing profile with the new data
            serializer.update(existing_profile, serializer.validated_data)
            return Response({'message': 'UserProfile updated successfully.'}, status=200)
        else:
            # If no profile exists, create a new one
            serializer.save(user=self.request.user)
            return Response({'message': 'UserProfile created successfully.'}, status=201)


class UserProfileByUserView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = [TokenAuthentication]

    def get_user_from_token(self, request):
        print('searching')
        # Extract user from the authentication token
        user, _ = TokenAuthentication().authenticate(request)
        return user

    def get_object(self):
        # Retrieve the profile picture for the current user
        user = self.get_user_from_token(self.request)
        return get_object_or_404(UserProfile, user=user)


class UserProfileDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id', None)

        if user_id is not None:
            try:
                # Delete all UserProfile entries for the specified user ID
                UserProfile.objects.filter(user_id=user_id).delete()
                return Response({'message': 'All entries for the user deleted successfully.'}, status=200)
            except UserProfile.DoesNotExist:
                return Response({'error': 'User profile not found.'}, status=404)
        else:
            return Response({'error': 'User ID not provided.'}, status=400)