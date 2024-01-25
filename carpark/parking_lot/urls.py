from django.urls import path
from .views import ParkingLotListCreateView, ParkingLotRetrieveUpdateDestroyView

urlpatterns = [
    path('parking-lot/', ParkingLotListCreateView.as_view(), name='parking-lots-list-create'),
    path('parking-lot/<int:id>/', ParkingLotRetrieveUpdateDestroyView.as_view(), name='parking-lot-detail'),
]