from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny
from .models import UserProfile
from .serializers import UserProfileSerializer, UserProfileTokenSerializer
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


class UserProfileByUserView(generics.GenericAPIView):
    serializer_class = UserProfileTokenSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Validate the input serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract the token from the validated data
        token = serializer.validated_data['token']
        print(f'Received token: {token}')
        
        # Create a mock request with the token in the headers for authentication
        request.META['HTTP_AUTHORIZATION'] = f'Token {token}'
        print(f'Request headers: {request.META["HTTP_AUTHORIZATION"]}')
        
        # Authenticate the user
        user, auth_token = TokenAuthentication().authenticate(request)
        if not user:
            raise ValidationError("Invalid token")
        
        print(f'Authenticated user: {user}, token: {auth_token}')
        
        # Retrieve the user profile
        profile = get_object_or_404(UserProfile, user=user)
        print(f'User profile found: {profile}')
        
        # Serialize the user profile
        profile_serializer = UserProfileSerializer(profile)
        return Response(profile_serializer.data, status=status.HTTP_200_OK)


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