from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q
from .models import ParkingExit
from .serializers import ParkingExitSerializer
from parking_invoice.models import ParkingInvoice
from parking_lot.models import ParkingLot
# Create your views here.

class CreateParkingExitView(generics.CreateAPIView):
    queryset = ParkingExit.objects.all()
    serializer_class = ParkingExitSerializer

    def perform_create(self, serializer):
        license_plate = serializer.validated_data['license_plate']
        parking_lot = serializer.validated_data['parking_lot']
        unpaid_invoices = ParkingInvoice.objects.filter(
            parking_lot=parking_lot,
            license_plate=license_plate,
            is_paid=False
        )
        if unpaid_invoices.exists():
            raise ValidationError("There are unpaid invoices for this license plate.")
        serializer.save()

class TodayParkingExitsView(APIView):
    def get(self, request, *args, **kwargs):
        today = timezone.now().date()
        parking_lot = ParkingLot.objects.get(street_address=request.query_params.get('street_address'))
        exits = ParkingExit.objects.filter(timestamp__date=today, parking_lot=parking_lot)
        serializer = ParkingExitSerializer(exits, many=True)
        return Response(serializer.data)
