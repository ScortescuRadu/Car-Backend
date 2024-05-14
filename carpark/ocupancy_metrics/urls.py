from django.urls import path
from .views import AdjustOccupancyView, OccupancyMetricsByAddressView

urlpatterns = [
    path('adjust/', AdjustOccupancyView.as_view(), name='adjust-occupancy'),
    path('by-address/', OccupancyMetricsByAddressView.as_view(), name='occupancy-metrics'),
]
