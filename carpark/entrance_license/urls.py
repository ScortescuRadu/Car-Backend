from django.urls import path
from .views import CreateParkingEntranceView, TodayParkingEntrancesView

urlpatterns = [
    path('create-entrance/', CreateParkingEntranceView.as_view(), name='create-entrance'),
    path('today-entrances/', TodayParkingEntrancesView.as_view(), name='today-entrances'),
]