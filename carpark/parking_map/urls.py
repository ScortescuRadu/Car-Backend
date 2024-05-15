from django.urls import path
from .views import ParkingLotTileListCreate
urlpatterns = [
    path('map/', ParkingLotTileListCreate.as_view(), name='tile-list-create'),
]