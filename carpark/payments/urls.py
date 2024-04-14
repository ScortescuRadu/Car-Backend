from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import CreateCheckoutSession, WebHookView, PaymentSheetView, CSRFTokenView, CreateWebCheckoutSessionView

urlpatterns = [
    path('get-csrf-token/', CSRFTokenView.as_view(), name='get_csrf_token'),
    path('payment-sheet/', PaymentSheetView.as_view(), name='stripe-payment'),
    path('checkout/', CreateCheckoutSession.as_view(), name='stripe-checkout'),
    path('webhook-test/', WebHookView.as_view(), name='stripe-test'),
    path('web/checkout/' , CreateWebCheckoutSessionView.as_view(), name='stripe-web-checkout'), 
]