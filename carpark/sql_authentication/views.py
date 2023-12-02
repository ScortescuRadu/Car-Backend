from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.schemas.openapi import AutoSchema
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .serializers import UserProfileSerializer

@swagger_auto_schema(
    method='POST',  # Specify the HTTP method
    operation_id='user_registration',
    operation_description='Register a new user',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username for registration'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD, description='Password for registration'),
            # Add other fields from your UserProfileSerializer as needed
        },
        required=['username', 'password'],  # Add required fields
        example={
            'username': 'new_user',
            'password': 'secure_password',
            # Add other example fields from your UserProfileSerializer as needed
        }
    ),
    responses={
        201: 'User created successfully',
        400: 'Bad Request',
    },
)
@permission_classes([AllowAny])
@api_view(['POST'])
def user_registration(request):
    """
    Register a new user.
    """
    serializer = UserProfileSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='POST',  # Specify the HTTP method
    operation_id='user_login',
    operation_description='Log in as an existing user',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username for login'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD, description='Password for login'),
        },
        example={
            'username': 'your_username',
            'password': 'your_password',
        }
    ),
    responses={
        200: 'Login successful',
        401: 'Invalid credentials',
    },
)
@permission_classes([AllowAny])
@api_view(['POST'])
def user_login(request):
    """
    Log in as an existing user.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    print(f'Login attempt: Username - {username}, Password - {password}')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
    return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
