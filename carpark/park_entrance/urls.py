from django.urls import path
from .views import ParkEntranceListCreateView

urlpatterns = [
    path('park-entrance/', ParkEntranceListCreateView.as_view(), name='park-entrance-list-create'),
]