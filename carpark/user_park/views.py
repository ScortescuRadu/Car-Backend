from django.shortcuts import render
from rest_framework import generics
from .models import UserPark
from .serializers import UserParkSerializer

# Create your views here.

class UserParkListCreateView(generics.ListCreateAPIView):
    queryset = UserPark.objects.all()
    serializer_class = UserParkSerializer