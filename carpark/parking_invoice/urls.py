from django.urls import path
from .views import ParkingInvoiceCreateView, UnpaidInvoicesListView, PaidInvoicesListView, ParkingInvoiceCountView, UnpaidInvoicesByLicensePlateView, CalculatePriceView

urlpatterns = [
    # Other URL patterns
    path('create/', ParkingInvoiceCreateView.as_view(), name='parking_invoice_create'),
    path('unpaid/', UnpaidInvoicesListView.as_view(), name='unpaid_invoices_list'),
    path('paid/', PaidInvoicesListView.as_view(), name='paid_invoices_list'),
    path('count/', ParkingInvoiceCountView.as_view(), name='count_existing_invoices'),
    path('license/unpaid/', UnpaidInvoicesByLicensePlateView.as_view(), name='unpaid-invoices-by-license'),
    path('calculate-price/', CalculatePriceView.as_view(), name='calculate_price'),
]