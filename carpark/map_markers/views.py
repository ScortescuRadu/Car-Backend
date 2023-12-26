from django.shortcuts import render
from rest_framework import viewsets
from .models import Marker, Subscription
from .serializers import MarkerSerializer, MarkersListSerializer, SubscriptionSerializer
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


# GET all Markers
class MarkerListView(generics.ListAPIView):
    queryset = Marker.objects.all()
    serializer_class = MarkersListSerializer


class SubscribeToMarkerAPIView(APIView):
    def post(self, request, marker_id):
        user = request.user  # Assuming the user is authenticated
        marker = get_object_or_404(Marker, pk=marker_id)

        if not marker.is_subscribed:
            if not Subscription.objects.filter(user=user, marker=marker).exists():
                serializer = SubscriptionSerializer(data={'user': user.id, 'marker': marker.id})
                if serializer.is_valid():
                    serializer.save()
                    marker.is_subscribed = True
                    marker.save()
                    return Response({'success': True, 'message': 'Subscription successful'}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'success': False, 'message': 'Invalid serializer data'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'success': False, 'message': 'User is already subscribed to the marker'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'success': False, 'message': 'Marker is already subscribed'}, status=status.HTTP_400_BAD_REQUEST)