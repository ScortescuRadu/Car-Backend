from django.shortcuts import render
from rest_framework import viewsets
from .models import Marker
from .serializers import MarkerSerializer, MarkersListSerializer
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response

# Create your views here.

class MarkerView(generics.CreateAPIView):
    queryset = Marker.objects.all()
    serializer_class = MarkerSerializer

    def create(self, request, *args, **kwargs):
        # Check if a marker with the same latitude and longitude already exists
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        if Marker.objects.filter(latitude=latitude, longitude=longitude).exists():
            return Response(
                {'detail': 'Marker with the same latitude and longitude already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().create(request, *args, **kwargs)

class MarkerListView(generics.ListAPIView):
    queryset = Marker.objects.all()
    serializer_class = MarkersListSerializer