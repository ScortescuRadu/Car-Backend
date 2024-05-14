from django.urls import path
from .views import AdjustIncomeView, IncomeMetricsByAddressView

urlpatterns = [
    path('adjust/', AdjustIncomeView.as_view(), name='adjust-income'),
    path('by-address/', IncomeMetricsByAddressView.as_view(), name='income-metrics'),
]