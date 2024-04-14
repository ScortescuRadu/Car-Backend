from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication 
from django.middleware.csrf import get_token
from .models import ParkingInvoice
from .serializers import ParkingInvoiceSerializer, LicensePlateSerializer, ParkingInvoiceOutputSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from datetime import timedelta
from django.utils import timezone
from django.http import Http404

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
        print('ha')
        user = self.get_user_from_token(self.request)
        print(user)
        print(user.id)
        user_id = user.id if user else None

        # Set additional fields before saving
        serializer.save(user_id=user_id, timestamp=timezone.now(), is_paid=False)

    def create(self, request, *args, **kwargs):
        print('aha')
        user = self.get_user_from_token(request)
        print(user)

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
        user_id = user.id if user else None
        unpaid_invoices = ParkingInvoice.objects.filter(user_id=user_id, is_paid=False)

        # Update time_spent for each invoice
        current_timestamp = timezone.now()
        print(current_timestamp)
        for invoice in unpaid_invoices:
            time_spent = (current_timestamp - invoice.timestamp).total_seconds() / 3600  # Convert to hours
            invoice.time_spent = time_spent
            invoice.save()

        return unpaid_invoices


class PaidInvoicesListView(generics.ListAPIView):
    serializer_class = ParkingInvoiceSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.id if self.request.user else None
        print(user_id)
        recent_param = self.request.headers.get('Recent')
        print(recent_param)

        if recent_param == -1:
            return ParkingInvoice.objects.filter(user_id=user_id, is_paid=True)
        else:
            print(recent_param)
            recent_time = timezone.now() - timedelta(days=int(recent_param))
            print(recent_time)
            return ParkingInvoice.objects.filter(user_id=user_id, is_paid=False, timestamp__gte=recent_time)


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
