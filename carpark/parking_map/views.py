from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import ParkingLotTile
from .serializers import ParkingLotTileSerializer
from parking_lot.models import ParkingLot
# Create your views here.

class ParkingLotTileListCreate(generics.ListCreateAPIView):
    serializer_class = ParkingLotTileSerializer

    def get_queryset(self):
        street_address = self.request.query_params.get('street_address')
        if not street_address:
            raise ValidationError('street_address is required.')

        try:
            parking_lot = ParkingLot.objects.get(street_address=street_address)
            return ParkingLotTile.objects.filter(parking_lot=parking_lot)
        except ParkingLot.DoesNotExist:
            raise ValidationError('ParkingLot with the given street address does not exist.')

    def create(self, request, *args, **kwargs):
        street_address = request.data.get('street_address')
        if not street_address:
            raise ValidationError('street_address is required.')
        
        try:
            parking_lot = ParkingLot.objects.get(street_address=street_address)
        except ParkingLot.DoesNotExist:
            raise ValidationError('ParkingLot with the given street address does not exist.')

        data = request.data.copy()
        tiles_data = data.get('tiles_data')

        if not tiles_data:
            raise ValidationError('tiles_data is required.')

        parking_lot_tile, created = ParkingLotTile.objects.get_or_create(parking_lot=parking_lot)
        parking_lot_tile.tiles_data = tiles_data
        parking_lot_tile.save()

        serializer = self.get_serializer(parking_lot_tile)
        return Response(serializer.data, status=201)
