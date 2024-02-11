from django.shortcuts import render
from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import UserStripe
from .serializers import UserStripeSerializer
import stripe

# Set your Stripe API key
stripe.api_key = 'sk_test_51OgVJzLevPehYIou9TNWxRxzwD1GLGeo4jKYcXCO5wp59aCLuoBd6vsqQwANcnZVE0k4QwCuYm1b3oEuSz3NJYmf00qHRz9I8C'

# Create your views here.

class UserStripeView(generics.RetrieveUpdateAPIView):
    queryset = UserStripe.objects.all()
    serializer_class = UserStripeSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_user_from_token(self, request):
        # Extract user from the authentication token
        user, _ = TokenAuthentication().authenticate(request)
        return user

    def get_object(self, request, *args, **kwargs):
        # Check if a profile picture already exists for the user
        user = self.get_user_from_token(request)
        obj, created = UserStripe.objects.get_or_create(user=user)
        return obj

    def perform_update(self, serializer):
        # Perform the update and create the Stripe customer if not already created
        user_stripe = serializer.save()

        if user_stripe.stripe_customer_id is None:
            # Create a new Stripe customer
            stripe_customer = stripe.Customer.create()
            user_stripe.stripe_customer = stripe_customer.id
            user_stripe.save()
