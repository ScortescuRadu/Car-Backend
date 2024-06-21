from django.urls import path
from .views import CreateParkingExitView, TodayParkingExitsView

urlpatterns = [
    path('create-exit/', CreateParkingExitView.as_view(), name='create-exit'),
    path('today-exits/', TodayParkingExitsView.as_view(), name='today-exits'),
]