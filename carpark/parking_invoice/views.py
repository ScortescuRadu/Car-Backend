from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication 
from django.middleware.csrf import get_token
from .models import ParkingInvoice
from .serializers import ParkingInvoiceSerializer, LicensePlateSerializer, ParkingInvoiceOutputSerializer, PriceCalculationInputSerializer, PriceOutputSerializer, ParkingInvoiceReservationSerializer, ParkingInvoiceAddressSerializer
from user_profile.models import UserProfile
from parking_lot.models import ParkingLot
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from datetime import timedelta
from django.utils import timezone
from django.http import Http404
from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
import json

# Create your views here.

class ParkingInvoiceCreateView(generics.CreateAPIView):
    serializer_class = ParkingInvoiceSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_user_from_token(self, request):
        try:
            user, _ = TokenAuthentication().authenticate(request)
            return user
        except Exception as e:
            print(f"Error retrieving user: {str(e)}")
            return None

    def perform_create(self, serializer):
        user = self.get_user_from_token(self.request)
        user = user if user else None

        # Set additional fields before saving
        serializer.save(user=user, timestamp=timezone.now(), is_paid=False)

    def create(self, request, *args, **kwargs):
        user = self.get_user_from_token(request)

        if user is None:
            # Handle the case where the user is not found based on the token
            return Response({'error': 'User not found based on token'}, status=status.HTTP_401_UNAUTHORIZED)
        print('anah')

         # Log the request data for debugging
        print('Request Data:', request.data)
        response = super().create(request, *args, **kwargs)

        return response


class UnpaidInvoicesListView(generics.ListAPIView):
    serializer_class = ParkingInvoiceSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_user_from_token(self, request):
        try:
            # Extract user from the authentication token
            user, _ = TokenAuthentication().authenticate(request)
            return user
        except Exception as e:
            # Handle the case where the user is not found based on the token
            print(f"Error retrieving user: {str(e)}")
            return None

    def get_queryset(self):
        user = self.get_user_from_token(self.request)
        if user is None:
            return ParkingInvoice.objects.none()

        unpaid_invoices = ParkingInvoice.objects.filter(
            user=user, 
            is_paid=False
        ).select_related('parking_lot')

        # Calculate time spent for each invoice on the fly and do not save it
        current_timestamp = timezone.now()
        for invoice in unpaid_invoices:
            time_spent = (current_timestamp - invoice.timestamp).total_seconds() / 3600
            invoice.time_spent = time_spent

        return unpaid_invoices


class PaidInvoicesListView(generics.ListAPIView):
    serializer_class = ParkingInvoiceSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user if self.request.user else None
        print(user)
        recent_param = self.request.headers.get('Recent')
        print(recent_param)

        if recent_param == -1:
            return ParkingInvoice.objects.filter(user=user, is_paid=True)
        else:
            print(recent_param)
            recent_time = timezone.now() - timedelta(days=int(recent_param))
            print(recent_time)
            return ParkingInvoice.objects.filter(user=user, is_paid=False, timestamp__gte=recent_time)


class ParkingInvoiceCountView(generics.ListAPIView):
    serializer_class = ParkingInvoiceSerializer

    def get_queryset(self):
        return ParkingInvoice.objects.filter(is_paid=True)

    def list(self, request, *args, **kwargs):
        count = self.get_queryset().count()
        return Response({"paid_count": count})


class UnpaidInvoicesByLicensePlateView(generics.ListAPIView):
    serializer_class = LicensePlateSerializer

    def post(self, request, *args, **kwargs):
        """
        Receives a POST request with a license plate in the body, validates it,
        and returns all unpaid invoices for that license plate using a different output serializer.
        """
        # Deserialize input
        input_serializer = self.get_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        license_plate = input_serializer.validated_data['license_plate']

        # Filter the queryset based on the validated license plate
        queryset = ParkingInvoice.objects.filter(license_plate=license_plate, is_paid=False)

        # Use a different serializer for the output data
        output_serializer = ParkingInvoiceOutputSerializer(queryset, many=True)
        return Response(output_serializer.data)

    def get_queryset(self):
        """
        Override to provide a default or context-specific queryset.
        """
        if self.request.method == 'GET':
            # Optionally handle GET requests differently, or raise an exception if GET is not supported.
            raise Http404("GET method is not supported on this endpoint")
        # Default empty queryset for POST if needed prior to filtering.
        return ParkingInvoice.objects.none()

    def get_serializer_class(self):
        """
        Optionally, provide different serializer classes for different actions.
        """
        if self.request.method.lower() == 'post':
            return LicensePlateSerializer
        return ParkingInvoiceOutputSerializer  # Default to output serializer for any other methods


class CalculatePriceView(GenericAPIView):
    serializer_class = PriceCalculationInputSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            license_plate = serializer.validated_data['license_plate']
            timestamp = serializer.validated_data['timestamp']
            try:
                invoice = ParkingInvoice.objects.filter(license_plate=license_plate, is_paid=False).first()
                time_difference = timezone.now() - timestamp
                hours_spent = max(round(time_difference.total_seconds() / 3600), 1)
                price = Decimal(invoice.hourly_price * hours_spent).quantize(Decimal('0.01'))
                output_serializer = PriceOutputSerializer({'price': price})
                return Response(output_serializer.data, status=status.HTTP_200_OK)
            except ParkingInvoice.DoesNotExist:
                return Response({'error': "No unpaid invoice found for this license plate."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateReservationView(generics.CreateAPIView):
    queryset = ParkingInvoice.objects.all()
    serializer_class = ParkingInvoiceReservationSerializer

    def post(self, request, *args, **kwargs):
        address = self.request.data.get('address')
        license_plate = self.request.data.get('license_plate')
        token = self.request.data.get('token')

        # Attempt to authenticate user by token
        if token:
            user = self.request.user if self.request.user.is_authenticated else None
            if user is None and token:
                try:
                    user = Token.objects.get(key=token).user
                except Token.DoesNotExist:
                    print('user not found')
            if user:
                user = user
        else:
            # Try to find user by license plate
            try:
                user_profile = UserProfile.objects.get(car_id=license_plate)
                user = user_profile.user
            except UserProfile.DoesNotExist:
                user = 0  # No user found, use default value

        try:
            parking_lot = ParkingLot.objects.get(street_address=address)
        except ParkingLot.DoesNotExist:
            return Response({'error': 'Parking lot not found.'}, status=status.HTTP_404_NOT_FOUND)

        invoice_data = {
            'user': user,
            'parking_lot': parking_lot,
            'license_plate': license_plate,
            'reserved_time': True,
            'hourly_price': parking_lot.price,
            'spot_description': 'default value for testing'
        }

        serializer = self.get_serializer(data=invoice_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ParkingInvoiceListView(generics.CreateAPIView):
    queryset = ParkingInvoice.objects.all()
    serializer_class = ParkingInvoiceAddressSerializer
    authentication_classes = [TokenAuthentication]

    def post(self, request, *args, **kwargs):
        selected_address = self.request.data.get('selectedAddress')
        time_frame = self.request.data.get('timeFrame')
        if not selected_address:
            return Response({"error": "selectedAddress is required"}, status=400)

        parking_lot = get_object_or_404(ParkingLot, street_address=selected_address)

        if time_frame == 'today':
            start_time = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_frame == 'lastWeek':
            start_time = timezone.now() - timedelta(days=7)
        elif time_frame == 'lastMonth':
            start_time = timezone.now() - timedelta(days=30)
        else:
            start_time = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        invoices = ParkingInvoice.objects.filter(parking_lot=parking_lot, timestamp__gte=start_time)

        serializer = ParkingInvoiceSerializer(invoices, many=True)
        return Response(serializer.data)


class ParkingInvoiceDeleteView(APIView):
    authentication_classes = [TokenAuthentication]

    def delete(self, request, *args, **kwargs):
        parking_lot_address = request.data.get('parking_lot')
        timestamp = request.data.get('timestamp')
        license_plate = request.data.get('license_plate')

        if not parking_lot_address or not timestamp or not license_plate:
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            parking_lot = ParkingLot.objects.get(street_address=parking_lot_address)
        except ParkingLot.DoesNotExist:
            return Response({'error': 'Parking lot not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            invoice = ParkingInvoice.objects.get(
                parking_lot=parking_lot,
                timestamp=timestamp,
                license_plate=license_plate
            )
            invoice.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ParkingInvoice.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)


class CreateInvoiceView(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request, *args, **kwargs):
        address = request.data.get('address')
        token = request.data.get('token')

        if not address or not token:
            return Response({'error': 'Address and token are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
        except Token.DoesNotExist:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            parking_lot = ParkingLot.objects.get(street_address=address)
        except ParkingLot.DoesNotExist:
            return Response({'error': 'Parking lot not found.'}, status=status.HTTP_404_NOT_FOUND)

        invoice_data = {
            'user': user.id,
            'parking_lot': parking_lot.id,
            'hourly_price': parking_lot.price,
            'spot_description': 'Default description',
            'license_plate': 'ABC123',  # This should be replaced with actual license plate if available
            'timestamp': timezone.now(),
        }

        serializer = ParkingInvoiceSerializer(data=invoice_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)