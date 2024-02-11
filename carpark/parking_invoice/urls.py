from django.urls import path
from .views import ParkingInvoiceCreateView, UnpaidInvoicesListView, PaidInvoicesListView

urlpatterns = [
    # Other URL patterns
    path('create/', ParkingInvoiceCreateView.as_view(), name='parking_invoice_create'),
    path('unpaid/', UnpaidInvoicesListView.as_view(), name='unpaid_invoices_list'),
    path('paid/', PaidInvoicesListView.as_view(), name='paid_invoices_list'),
]