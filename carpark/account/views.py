from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
import jwt, datetime
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
# from django.contrib.auth.models import User
from .models import User
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from django.middleware.csrf import get_token

from .serializers import UserSerializer, TokenInputSerializer, LogoutSerializer
from .models import BlacklistedToken

class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(email=request.data['email'])
            user.set_password(request.data['password'])
            user.save()
            token = Token.objects.create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        user = get_object_or_404(User, email=request.data['email'])

        if not user.check_password(request.data['password']):
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        token, created = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)

class UserInfoView(generics.GenericAPIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = TokenInputSerializer

    def post(self, request, *args, **kwargs):
        serializer = TokenInputSerializer(data=request.data)
        
        if serializer.is_valid():
            token_key = serializer.validated_data.get('token')
            
            # Retrieve user_id associated with the token
            try:
                user_id = Token.objects.get(key=token_key).user_id
                user = User.objects.get(id=user_id)
                
                return Response({'user': user.email})
            except Token.DoesNotExist:
                return Response({'error': 'Invalid token'}, status=400)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=400)
        else:
            return Response({'error': 'Invalid input'}, status=400)

class LogoutView(generics.CreateAPIView):
    serializer_class = LogoutSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        token = request.data.get('token', None)
        
        if not token:
            return Response({'error': 'Token not provided'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        authenticated_user = user.is_authenticated

        # Ensure the user is authenticated before blacklisting the token
        if authenticated_user:
            # Blacklist the token
            BlacklistedToken.objects.create(user=user, token=token)
        
        # Delete the token (if it exists)
        try:
            token_obj = Token.objects.get(key=token)
            token_obj.delete()
        except Token.DoesNotExist:
            response_data = {
                'message': 'Token does not exist.'
            }
            return Response(response_data, status=status.HTTP_200_OK)

        response_data = {
            'message': 'Logout successful. Token blacklisted.'
        }
        return Response(response_data, status=status.HTTP_200_OK)

class CSRFTokenView(APIView):
    """
    API View to retrieve a CSRF token.
    """

    def get(self, request, *args, **kwargs):
        # get_token(request) generates or retrieves a CSRF token
        csrf_token = get_token(request)
        return Response({'csrfToken': csrf_token})
