from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework import generics
from .models import ParkingLot
from user_park.models import UserPark
from city.models import City
from .serializers import (ParkingLotSerializer,
    UserParkingLotSerializer,
    UserParkInputSerializer,
    UserParkOutputSerializer,
    TestParkingLotSerializer,
    StreetAddressSerializer,
    CityNameSerializer,
    UserParkAddressInputSerializer,
    ParkPriceUpdateSerializer,
    ParkPhoneUpdateSerializer,
    ParkTimesUpdateSerializer,
    ParkCapacityUpdateSerializer,
    ParkAddressUpdateSerializer)
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


class ParkingLotByCityView(generics.ListAPIView):
    serializer_class_input = CityNameSerializer
    serializer_class_output = StreetAddressSerializer

    def get_serializer_class(self):
        # This method dynamically selects a serializer class based on the HTTP method
        if self.request.method == 'POST':
            return self.serializer_class_input
        elif self.request.method == 'GET':
            return self.serializer_class_output
        return super().get_serializer_class()

    def get_queryset(self):
        # Since we do not use GET for listing in this view, we return an empty queryset
        return ParkingLot.objects.none()

    def post(self, request, *args, **kwargs):
        # Correct use of class attribute with `self`
        input_serializer = self.get_serializer(data=request.data)  # This will call get_serializer_class
        if input_serializer.is_valid():
            city_name = input_serializer.validated_data['city_name']
            try:
                city = City.objects.get(name__iexact=city_name)  # Case-insensitive search for city name
            except City.DoesNotExist:
                raise NotFound(detail=f"City with name {city_name} does not exist.")
            
            parking_lots = ParkingLot.objects.filter(city=city, street_address__isnull=False)
            output_serializer = self.serializer_class_output(parking_lots, many=True)  # Use class attribute with `self`
            return Response(output_serializer.data)
        else:
            raise ValidationError(input_serializer.errors)


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


class UserParkingLotDataView(generics.ListAPIView):
    serializer_class_input = UserParkAddressInputSerializer
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
            street_address = serializer_input.validated_data['street_address']

            if not user_token:
                return Response({'error': 'Token not provided'}, status=status.HTTP_400_BAD_REQUEST)

            # Validate the user ID from the token
            try:
                user_id = Token.objects.get(key=user_token).user_id
            except Token.DoesNotExist:
                return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

            # Retrieve the ParkingLot corresponding to the street address
            try:
                parking_lot = ParkingLot.objects.get(street_address=street_address)
            except ParkingLot.DoesNotExist:
                raise NotFound("Parking lot not found for the provided street address")

            # Return the ParkingLot details
            serializer_output = self.serializer_class_output(parking_lot)
            return Response(serializer_output.data)

        except Exception as e:
            # Log the exception for debugging purposes
            print(f"An unexpected error occurred: {str(e)}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ParkingLotEditPrice(generics.CreateAPIView):
    queryset = ParkingLot.objects.all()
    serializer_class = ParkPriceUpdateSerializer

    def create(self, request, *args, **kwargs):
        try:
            user_token = request.data.get('token')
            price = request.data.get('price')
            street_address = request.data.get('street_address')

            # Extract the user ID from the token
            try:
                user_id = Token.objects.get(key=user_token).user_id
            except Token.DoesNotExist:
                return Response({'error': f'Invalid token {user_token}'}, status=status.HTTP_401_UNAUTHORIZED)

            # Retrieve the ParkingLot corresponding to the street address
            try:
                parking_lot = ParkingLot.objects.get(street_address=street_address)
            except ParkingLot.DoesNotExist:
                raise NotFound("Parking lot not found for the provided street address")

            # Update the price of the parking lot
            parking_lot.price = price
            parking_lot.save()

            return Response({'message': 'Parking lot price changed successfully'}, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Log the exception for debugging purposes
            print(f"An unexpected error occurred: {str(e)}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ParkingLotEditPhone(generics.CreateAPIView):
    queryset = ParkingLot.objects.all()
    serializer_class = ParkPhoneUpdateSerializer

    def create(self, request, *args, **kwargs):
        try:
            user_token = request.data.get('token')
            phone = request.data.get('phone')
            street_address = request.data.get('street_address')

            # Extract the user ID from the token
            try:
                user_id = Token.objects.get(key=user_token).user_id
            except Token.DoesNotExist:
                return Response({'error': f'Invalid token {user_token}'}, status=status.HTTP_401_UNAUTHORIZED)

            # Retrieve the ParkingLot corresponding to the street address
            try:
                parking_lot = ParkingLot.objects.get(street_address=street_address)
            except ParkingLot.DoesNotExist:
                raise NotFound("Parking lot not found for the provided street address")

            # Update the phone number of the parking lot
            parking_lot.phone_number = phone
            parking_lot.save()

            return Response({'message': 'Parking lot phone number changed successfully'}, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Log the exception for debugging purposes
            print(f"An unexpected error occurred: {str(e)}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ParkingLotEditTimes(generics.CreateAPIView):
    queryset = ParkingLot.objects.all()
    serializer_class = ParkTimesUpdateSerializer

    def create(self, request, *args, **kwargs):
        try:
            user_token = request.data.get('token')
            times = request.data.get('times')
            street_address = request.data.get('street_address')

            # Extract the user ID from the token
            try:
                user_id = Token.objects.get(key=user_token).user_id
            except Token.DoesNotExist:
                return Response({'error': f'Invalid token {user_token}'}, status=status.HTTP_401_UNAUTHORIZED)

            # Retrieve the ParkingLot corresponding to the street address
            try:
                parking_lot = ParkingLot.objects.get(street_address=street_address)
            except ParkingLot.DoesNotExist:
                raise NotFound("Parking lot not found for the provided street address")

            # Update the opening and closing times of the parking lot
            parking_lot.weekday_opening_time = times.get('weekdayOpening')
            parking_lot.weekday_closing_time = times.get('weekdayClosing')
            parking_lot.weekend_opening_time = times.get('weekendOpening')
            parking_lot.weekend_closing_time = times.get('weekendClosing')
            parking_lot.save()

            return Response({'message': 'Parking lot times changed successfully'}, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Log the exception for debugging purposes
            print(f"An unexpected error occurred: {str(e)}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ParkingLotEditCapacity(generics.CreateAPIView):
    queryset = ParkingLot.objects.all()
    serializer_class = ParkCapacityUpdateSerializer

    def create(self, request, *args, **kwargs):
        try:
            user_token = request.data.get('token')
            capacity = request.data.get('capacity')
            street_address = request.data.get('street_address')

            # Extract the user ID from the token
            try:
                user_id = Token.objects.get(key=user_token).user_id
            except Token.DoesNotExist:
                return Response({'error': f'Invalid token {user_token}'}, status=status.HTTP_401_UNAUTHORIZED)

            # Retrieve the ParkingLot corresponding to the street address
            try:
                parking_lot = ParkingLot.objects.get(street_address=street_address)
            except ParkingLot.DoesNotExist:
                raise NotFound("Parking lot not found for the provided street address")

            # Update the capacity of the parking lot
            parking_lot.capacity = capacity
            parking_lot.save()

            return Response({'message': 'Parking lot capacity changed successfully'}, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Log the exception for debugging purposes
            print(f"An unexpected error occurred: {str(e)}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ParkingLotEditAddress(generics.CreateAPIView):
    queryset = ParkingLot.objects.all()
    serializer_class = ParkAddressUpdateSerializer

    def create(self, request, *args, **kwargs):
        try:
            user_token = request.data.get('token')
            new_address = request.data.get('new_address')
            new_latitude = request.data.get('new_latitude')
            new_longitude = request.data.get('new_longitude')
            street_address = request.data.get('street_address')

            # Extract the user ID from the token
            try:
                user_id = Token.objects.get(key=user_token).user_id
            except Token.DoesNotExist:
                return Response({'error': f'Invalid token {user_token}'}, status=status.HTTP_401_UNAUTHORIZED)

            # Retrieve the ParkingLot corresponding to the street address
            try:
                parking_lot = ParkingLot.objects.get(street_address=street_address)
            except ParkingLot.DoesNotExist:
                raise NotFound("Parking lot not found for the provided street address")

            # Update the address of the parking lot
            parking_lot.street_address = new_address
            parking_lot.latitude = new_latitude
            parking_lot.longitude = new_longitude
            parking_lot.save()

            return Response({'message': 'Parking lot address changed successfully'}, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Log the exception for debugging purposes
            print(f"An unexpected error occurred: {str(e)}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
