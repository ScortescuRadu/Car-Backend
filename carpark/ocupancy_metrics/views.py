from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import OccupancyMetrics
from income_metrics.serializers import AddressSerializer
from .serializers import OccupancyAdjustmentSerializer
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
                occupancy_metrics, metrics_created = OccupancyMetrics.objects.get_or_create(
                    parking_lot=parking_lot,
                    defaults={
                        'total_current_occupancy': 0,
                        'current_occupancy': {
                            'Monday': {f"{i:02d}:00": 0 for i in range(24)},
                            'Tuesday': {f"{i:02d}:00": 0 for i in range(24)},
                            'Wednesday': {f"{i:02d}:00": 0 for i in range(24)},
                            'Thursday': {f"{i:02d}:00": 0 for i in range(24)},
                            'Friday': {f"{i:02d}:00": 0 for i in range(24)},
                            'Saturday': {f"{i:02d}:00": 0 for i in range(24)},
                            'Sunday': {f"{i:02d}:00": 0 for i in range(24)}
                        },
                        'average_occupancy': {
                            'Monday': {f"{i:02d}:00": 0 for i in range(24)},
                            'Tuesday': {f"{i:02d}:00": 0 for i in range(24)},
                            'Wednesday': {f"{i:02d}:00": 0 for i in range(24)},
                            'Thursday': {f"{i:02d}:00": 0 for i in range(24)},
                            'Friday': {f"{i:02d}:00": 0 for i in range(24)},
                            'Saturday': {f"{i:02d}:00": 0 for i in range(24)},
                            'Sunday': {f"{i:02d}:00": 0 for i in range(24)}
                        }
                    }
                )
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
