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
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token

from .serializers import UserSerializer, TokenInputSerializer, LogoutSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(username=request.data['username'])
            user.set_password(request.data['password'])
            user.save()
            token = Token.objects.create(user=user)
            return Response({'token': token.key})
        return Response(serializer.errors, status=status.HTTP_200_OK)


class LoginView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        user = get_object_or_404(User, username=request.data['username'])
        if not user.check_password(request.data['password']):
            return Response("missing user", status=status.HTTP_404_NOT_FOUND)
        token, created = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user)
        return Response({'token': token.key})

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
                
                return Response({'user': user.username})
            except Token.DoesNotExist:
                return Response({'error': 'Invalid token'}, status=400)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=400)
        else:
            return Response({'error': 'Invalid input'}, status=400)

class LogoutView(generics.CreateAPIView):
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        response = self.create(request, *args, **kwargs)
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response

    def create(self, request, *args, **kwargs):
        return Response({'detail': 'Logout successful'})