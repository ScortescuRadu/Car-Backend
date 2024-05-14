from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import IncomeMetrics
from .serializers import IncomeAdjustmentSerializer, AddressSerializer
from parking_lot.models import ParkingLot

# Create your views here.

class AdjustIncomeView(APIView):
    serializer_class = IncomeAdjustmentSerializer

    def post(self, request, *args, **kwargs):
        serializer = IncomeAdjustmentSerializer(data=request.data)
        if serializer.is_valid():
            address = serializer.validated_data['street_address']
            amount = serializer.validated_data['amount']
            income_metrics = serializer.update_income_metrics(address, amount)
            return Response({'status': 'income updated', 'metrics_id': income_metrics.id})
        else:
            return Response(serializer.errors, status=400)


class IncomeMetricsByAddressView(generics.GenericAPIView):
    serializer_class = AddressSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            address = serializer.validated_data['street_address']
            try:
                parking_lot = ParkingLot.objects.get(street_address=address)
                income_metrics = IncomeMetrics.objects.get(parking_lot=parking_lot)
                response_data = {
                    'daily_current': income_metrics.daily_current,
                    'daily_average': income_metrics.daily_average,
                    'monthly_total': income_metrics.monthly_total,
                    'yearly_total': income_metrics.yearly_total
                }
                return Response(response_data)
            except ParkingLot.DoesNotExist:
                return Response({'error': 'Parking lot not found.'}, status=status.HTTP_404_NOT_FOUND)
            except IncomeMetrics.DoesNotExist:
                return Response({'error': 'Income metrics not found for this parking lot.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
