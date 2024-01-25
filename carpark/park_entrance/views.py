from django.shortcuts import render
from rest_framework import generics
from .models import ParkingEntrance
from .serializers import ParkEntranceSerializer

# Create your views here.

class ParkEntranceListCreateView(generics.ListCreateAPIView):
    queryset = ParkingEntrance.objects.all()
    serializer_class = ParkEntranceSerializer