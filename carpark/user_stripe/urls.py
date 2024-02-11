from django.urls import path
from .views import UserStripeView

urlpatterns = [
    path('customer/', UserStripeView.as_view(), name='user_stripe'),
]