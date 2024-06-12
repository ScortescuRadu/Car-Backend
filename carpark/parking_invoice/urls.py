from django.urls import path
from .views import (
    ParkingInvoiceCreateView,
    UnpaidInvoicesListView,
    PaidInvoicesListView,
    ParkingInvoiceCountView,
    UnpaidInvoicesByLicensePlateView,
    CalculatePriceView,
    CreateReservationView,
    ParkingInvoiceListView,
    ParkingInvoiceDeleteView)

urlpatterns = [
    # Other URL patterns
    path('create/', ParkingInvoiceCreateView.as_view(), name='parking_invoice_create'),
    path('unpaid/', UnpaidInvoicesListView.as_view(), name='unpaid_invoices_list'),
    path('paid/', PaidInvoicesListView.as_view(), name='paid_invoices_list'),
    path('count/', ParkingInvoiceCountView.as_view(), name='count_existing_invoices'),
    path('license/unpaid/', UnpaidInvoicesByLicensePlateView.as_view(), name='unpaid-invoices-by-license'),
    path('calculate-price/', CalculatePriceView.as_view(), name='calculate_price'),
    path('reserve/', CreateReservationView.as_view(), name='reserve'),
    path('by-lot/', ParkingInvoiceListView.as_view(), name='by-lot'),
    path('delete/', ParkingInvoiceDeleteView.as_view(), name='delete'),
]