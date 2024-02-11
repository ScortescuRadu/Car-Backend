from rest_framework import serializers
from .models import UserStripe

class UserStripeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStripe
        fields = ['user', 'stripe_customer']