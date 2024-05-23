from django.urls import path
from .views import ParkingSpotCreateView, ParkingSpotListView

urlpatterns = [
    path('create/', ParkingSpotCreateView.as_view(), name='create_spot'),
    path('by-address/', ParkingSpotListView.as_view(), name='parking_spots_by_address'),
]