from django.urls import path
from .views import ParkingLotListCreateView, ParkingLotRetrieveUpdateDestroyView, ParkingLotAddViewSet, UserParkingLotsView

urlpatterns = [
    path('parking-lot/', ParkingLotListCreateView.as_view(), name='parking-lots-list-create'),
    path('parking-lot/<int:id>/', ParkingLotRetrieveUpdateDestroyView.as_view(), name='parking-lot-detail'),
    path('user-parking/', ParkingLotAddViewSet.as_view(), name='parking-lot-detail'),
    path('user-parking-lots/', UserParkingLotsView.as_view(), name='parking-lot-detail'),
]