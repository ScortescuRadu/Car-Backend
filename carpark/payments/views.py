from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views import View
import json
import stripe

# Set your Stripe API key
stripe.api_key = 'sk_test_51OgVJzLevPehYIou9TNWxRxzwD1GLGeo4jKYcXCO5wp59aCLuoBd6vsqQwANcnZVE0k4QwCuYm1b3oEuSz3NJYmf00qHRz9I8C'

# Replace this with your Customer model and serializer
# from your_app.models import Customer
# from your_app.serializers import CustomerSerializer

# Create your views here.

class CSRFTokenView(View):
    def get(self, request, *args, **kwargs):
        csrf_token = get_token(request)
        return JsonResponse({'csrf_token': csrf_token})


class PaymentSheetView(View):
    def post(self, request, *args, **kwargs):
        # Assume you have a JSON payload with the necessary data
        data = json.loads(request.body)

        try:
            # Create a new customer
            customer = stripe.Customer.create()

            # Create an ephemeral key
            ephemeral_key = stripe.EphemeralKey.create(
                customer=customer.id,
                stripe_version='2023-10-16',
            )

            # Create a payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=200,
                currency='eur',
                customer=customer['id'],
            )

            # Return the necessary information in the response
            response_data = {
                'paymentIntent': payment_intent.client_secret,
                'ephemeralKey': ephemeral_key.secret,
                'customer': customer.id,
                'publishableKey': 'pk_test_51OgVJzLevPehYIouZmmqxgYdBsUpSCEAFopmpN4idvlaZzi4665AuXJRlnpX0p1mGKoP6VkDWLOfSt8OvlAc9Tt400bHgGIYUf'
            }

            return JsonResponse(response_data, status=200)

        except Exception as e:
            # Handle exceptions appropriately
            return JsonResponse({'error': str(e)}, status=500)


class CreateCheckoutSession(APIView):
  def post(self, request):
    dataDict = dict(request.data)
    price = dataDict['price'][0]
    product_name = dataDict['product_name'][0]
    try:
      checkout_session = stripe.checkout.Session.create(
        line_items =[{
        'price_data' :{
          'currency' : 'usd',  
            'product_data': {
              'name': product_name,
            },
          'unit_amount': price
        },
        'quantity' : 1
      }],
        mode= 'payment',
        success_url= FRONTEND_CHECKOUT_SUCCESS_URL,
        cancel_url= FRONTEND_CHECKOUT_FAILED_URL,
        )
      return redirect(checkout_session.url , code=303)
    except Exception as e:
        print(e)
        return Response(
            {'error': e},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class WebHookView(APIView):
  def post(self , request):
    event = None
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
      event = stripe.Webhook.construct_event(
        payload ,sig_header , webhook_secret
        )
    except ValueError as err:
        # Invalid payload
        raise err
    except stripe.error.SignatureVerificationError as err:
        # Invalid signature
        raise err

    # Handle the event
    if event.type == 'payment_intent.succeeded':
      payment_intent = event.data.object 
      print("--------payment_intent ---------->" , payment_intent)
    elif event.type == 'payment_method.attached':
      payment_method = event.data.object 
      print("--------payment_method ---------->" , payment_method)
    # ... handle other event types
    else:
      print('Unhandled event type {}'.format(event.type))

    return JsonResponse(success=True, safe=False)