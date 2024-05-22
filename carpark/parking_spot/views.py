from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import ParkingLot, ParkingSpot
from .serializers import ParkingSpotSerializer, ParkingSpotInputSerializer
from django.shortcuts import get_object_or_404

# Create your views here.

class ParkingSpotCreateView(generics.CreateAPIView):
    serializer_class = ParkingSpotInputSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_user_from_token(self, request):
        # Extract user from the authentication token
        user, _ = TokenAuthentication().authenticate(request)
        return user

    def create(self, request, *args, **kwargs):
        user = self.get_user_from_token(request)
        if not user:
            return Response({"detail": "Invalid token or user not found."}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        street_address = serializer.validated_data['street_address']

        # Find the parking lot by street address
        parking_lot = get_object_or_404(ParkingLot, street_address=street_address)

        # Create the parking spot
        parking_spot = ParkingSpot(
            parking_lot=parking_lot,
            level=serializer.validated_data['level'],
            sector=serializer.validated_data['sector'],
            number=serializer.validated_data['number'],
            is_occupied=serializer.validated_data['is_occupied']
        )
        parking_spot.save()

        return Response(ParkingSpotSerializer(parking_spot).data, status=status.HTTP_201_CREATED)