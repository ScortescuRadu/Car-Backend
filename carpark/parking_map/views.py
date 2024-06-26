from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import ParkingLotTile
from .serializers import ParkingLotTileSerializer
from parking_lot.models import ParkingLot
from parking_spot.models import ParkingSpot
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

        # Save the tiles data
        parking_lot_tile, created = ParkingLotTile.objects.get_or_create(parking_lot=parking_lot)
        parking_lot_tile.tiles_data = tiles_data
        parking_lot_tile.save()

        # Create parking spots for tiles of type 'parking'
        for position, tile in tiles_data.items():
            if tile['type'] == 'parking':
                # Check if a spot with the same level, sector, and number already exists
                existing_spot = ParkingSpot.objects.filter(
                    parking_lot=parking_lot,
                    level=1,
                    sector=tile['sector'],
                    number=tile['number']
                ).exists()

                if not existing_spot:
                    ParkingSpot.objects.create(
                        parking_lot=parking_lot,
                        level=1,
                        sector=tile['sector'],
                        number=tile['number'],
                        is_occupied=False
                    )

        serializer = self.get_serializer(parking_lot_tile)
        return Response(serializer.data, status=201)
