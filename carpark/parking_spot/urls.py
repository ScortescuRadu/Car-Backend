from django.urls import path
from .views import ParkingSpotCreateView

urlpatterns = [
    path('create/', ParkingSpotCreateView.as_view(), name='create_spot'),
]