from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import OccupancyMetrics
from .serializers import OccupancyAdjustmentSerializer, AddressSerializer
from parking_lot.models import ParkingLot

# Create your views here.

class AdjustOccupancyView(generics.GenericAPIView):
    serializer_class = OccupancyAdjustmentSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            address = serializer.validated_data['street_address']
            adjustment = serializer.validated_data['adjustment']
            occupancy_metrics = serializer.update_occupancy_metrics(address, adjustment)
            return Response({'status': 'occupancy updated', 'metrics_id': occupancy_metrics.id})
        else:
            return Response(serializer.errors, status=400)


class OccupancyMetricsByAddressView(generics.GenericAPIView):
    serializer_class = AddressSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            address = serializer.validated_data['street_address']
            try:
                parking_lot = ParkingLot.objects.get(street_address=address)
                occupancy_metrics = OccupancyMetrics.objects.get(parking_lot=parking_lot)
                response_data = {
                    'current_occupancy': occupancy_metrics.current_occupancy,
                    'average_occupancy': occupancy_metrics.average_occupancy
                }
                return Response(response_data)
            except ParkingLot.DoesNotExist:
                return Response({'error': 'Parking lot not found.'}, status=status.HTTP_404_NOT_FOUND)
            except OccupancyMetrics.DoesNotExist:
                return Response({'error': 'Occupancy metrics not found for this parking lot.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
