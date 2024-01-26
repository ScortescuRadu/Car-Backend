from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework import generics
from .models import ParkingLot
from user_park.models import UserPark
from .serializers import ParkingLotSerializer, UserParkingLotSerializer, UserParkInputSerializer, UserParkOutputSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from rest_framework.response import Response

# Create your views here.

class ParkingLotListCreateView(generics.ListCreateAPIView):
    queryset = ParkingLot.objects.all()
    serializer_class = ParkingLotSerializer


class ParkingLotRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ParkingLot.objects.all()
    serializer_class = ParkingLotSerializer
    lookup_field = 'id'


class ParkingLotAddViewSet(generics.CreateAPIView):
    queryset = ParkingLot.objects.all()
    serializer_class = UserParkingLotSerializer

    def create(self, request, *args, **kwargs):
        try:
            user_token = request.data.get('token')
            price = request.data.get('price')
            capacity = request.data.get('capacity')

            # Check if required fields are present in the request
            if not (user_token and price is not None and capacity is not None):
                raise ValueError('Missing required fields in the request')

            # Extract the user ID from the token
            try:
                user_id = Token.objects.get(key=user_token).user_id
            except Token.DoesNotExist:
                return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

            User = get_user_model()

            # Attempt to get the user by ID
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Create a new ParkingLot instance
            new_parking_lot = ParkingLot.objects.create(price=price, capacity=capacity)

            # Create a new UserPark entry
            UserPark.objects.create(user=user, parking_lot=new_parking_lot)

            return Response({'message': 'Parking lot created successfully'}, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Log the exception for debugging purposes
            print(f"An unexpected error occurred: {str(e)}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserParkingLotsView(generics.ListAPIView):
    serializer_class_input = UserParkInputSerializer
    serializer_class_output = UserParkOutputSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return self.serializer_class_input
        elif self.request.method == 'GET':
            return self.serializer_class_output
        return super().get_serializer_class()

    def get_queryset(self):
        return UserPark.objects.none()  # Empty queryset as this is not used for POST requests

    def post(self, request, *args, **kwargs):
        try:
            serializer_input = self.serializer_class_input(data=request.data)
            serializer_input.is_valid(raise_exception=True)

            user_token = serializer_input.validated_data['token']

            if not user_token:
                return Response({'error': 'Token not provided'}, status=status.HTTP_400_BAD_REQUEST)

            # Extract the user ID from the token
            try:
                user_id = Token.objects.get(key=user_token).user_id
            except Token.DoesNotExist:
                return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

            # Get the user's parking lots
            user_parks = UserPark.objects.filter(user_id=user_id)
            parking_lots = [user_park.parking_lot for user_park in user_parks]

            # Serialize the queryset using the output serializer class
            serializer_output = self.serializer_class_output(parking_lots, many=True)

            return Response(serializer_output.data)

        except Exception as e:
            # Log the exception for debugging purposes
            print(f"An unexpected error occurred: {str(e)}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)