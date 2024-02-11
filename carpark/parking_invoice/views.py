from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication 
from django.middleware.csrf import get_token
from .models import ParkingInvoice
from .serializers import ParkingInvoiceSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from datetime import timedelta
from django.utils import timezone

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