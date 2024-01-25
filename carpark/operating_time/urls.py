from django.urls import path
from .views import OperatingHoursListCreateView

urlpatterns = [
    path('operating-hours/', OperatingHoursListCreateView.as_view(), name='operating-hours-list-create'),
]