from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Q
from .models import ParkEntrance
from .serializers import ParkEntranceSerializer
from parking_lot.models import ParkingLot
# Create your views here.

class CreateParkingEntranceView(generics.CreateAPIView):
    queryset = ParkEntrance.objects.all()
    serializer_class = ParkEntranceSerializer

class TodayParkingEntrancesView(APIView):
    def get(self, request, *args, **kwargs):
        today = timezone.now().date()
        parking_lot = ParkingLot.objects.get(street_address=request.query_params.get('street_address'))
        entrances = ParkEntrance.objects.filter(timestamp__date=today, parking_lot=parking_lot)
        serializer = ParkEntranceSerializer(entrances, many=True)
        return Response(serializer.data)