from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework import generics
from .models import ParkingLot
from user_park.models import UserPark
from .serializers import ParkingLotSerializer, UserParkingLotSerializer, UserParkInputSerializer, UserParkOutputSerializer, TestParkingLotSerializer, StreetAddressSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from rest_framework.response import Response

# Create your views here.

class TestParkingLotAddView(generics.ListCreateAPIView):
    queryset = ParkingLot.objects.all()
    serializer_class = ParkingLotSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ParkingLotListCreateView(generics.ListCreateAPIView):
    queryset = ParkingLot.objects.all()
    serializer_class = ParkingLotSerializer


class ParkingLotRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ParkingLot.objects.all()
    serializer_class = ParkingLotSerializer
    lookup_field = 'id'


class UserStreetAddressListView(generics.ListAPIView):
    serializer_class = StreetAddressSerializer

    def get_queryset(self):
        try:
            user_token = self.request.query_params.get('token')

            # Extract the user based on the token
            user = self.request.user if self.request.user.is_authenticated else None
            if user is None and user_token:
                try:
                    user = Token.objects.get(key=user_token).user
                except Token.DoesNotExist:
                    return ParkingLot.objects.none()

            # Get all ParkingLots associated with the user
            user_parking_lots = UserPark.objects.filter(user=user).select_related('parking_lot')

            # Extract street addresses from the ParkingLots
            if user_parking_lots:
                street_addresses = [up.parking_lot.street_address for up in user_parking_lots]

                # Use a serializer to serialize the queryset
                serializer = StreetAddressSerializer(ParkingLot.objects.filter(street_address__in=street_addresses), many=True)

                return serializer.data

            else:
                return []

        except Exception as e:
            # Log the exception for debugging purposes
            print(f"An unexpected error occurred: {str(e)}")
            return []


class ParkingLotAddViewSet(generics.CreateAPIView):
    queryset = ParkingLot.objects.all()
    serializer_class = UserParkingLotSerializer

    def create(self, request, *args, **kwargs):
        try:
            user_token = request.data.get('token')
            price = request.data.get('price')
            capacity = request.data.get('capacity')
            iban = request.data.get('iban')
            phone_number = request.data.get('phone_number')
            weekday_opening_time = request.data.get('weekday_opening_time')
            weekday_closing_time = request.data.get('weekday_closing_time')
            weekend_opening_time = request.data.get('weekend_opening_time')
            weekend_closing_time = request.data.get('weekend_closing_time')
            street_address = request.data.get('street_address')

            # Extract the user ID from the token
            try:
                user_id = Token.objects.get(key=user_token).user_id
            except Token.DoesNotExist:
                return Response({'error': f'Invalid token {user_token}'}, status=status.HTTP_401_UNAUTHORIZED)

            User = get_user_model()

            # Attempt to get the user by ID
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Create a new ParkingLot instance
            new_parking_lot = ParkingLot.objects.create(price=price,
                capacity=capacity,
                iban=iban,
                phone_number=phone_number,
                weekday_opening_time=weekday_opening_time,
                weekday_closing_time=weekday_closing_time,
                weekend_opening_time=weekend_opening_time,
                weekend_closing_time=weekend_closing_time,
                street_address=street_address)

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