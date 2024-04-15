from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication 
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views import View
from user_stripe.models import UserStripe
from rest_framework import status
from django.utils.http import urlencode
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
    def get_user_from_token(self, request):
        try:
            # Extract user from the authentication token
            user, _ = TokenAuthentication().authenticate(request)
            return user
        except Exception as e:
            # Handle the case where the user is not found based on the token
            print(f"Error retrieving user: {str(e)}")
            return None

    def post(self, request, *args, **kwargs):
        # Assume you have a JSON payload with the necessary data
        data = json.loads(request.body)

        try:
            print('try')
            user = self.get_user_from_token(request)
            user_stripe, created = UserStripe.objects.get_or_create(user=user)

            # Use the existing stripe_customer if available
            if user_stripe.stripe_customer:
                customer_id = user_stripe.stripe_customer
                print('yes')
            else:
                print('no')
                # Create a new customer if stripe_customer_id is not available
                customer = stripe.Customer.create()
                customer_id = customer["id"]

                # Update the UserStripe entry with the new stripe_customer_id
                user_stripe.stripe_customer = customer_id
                user_stripe.save()

            # Create an ephemeral key
            ephemeral_key = stripe.EphemeralKey.create(
                customer=customer_id,
                stripe_version='2023-10-16',
            )

            # Create a payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=200,
                currency='eur',
                customer=customer_id,
            )

            # Return the necessary information in the response
            response_data = {
                'paymentIntent': payment_intent.client_secret,
                'ephemeralKey': ephemeral_key.secret,
                'customer': customer_id,
                'publishableKey': 'pk_test_51OgVJzLevPehYIouZmmqxgYdBsUpSCEAFopmpN4idvlaZzi4665AuXJRlnpX0p1mGKoP6VkDWLOfSt8OvlAc9Tt400bHgGIYUf'
            }

            return JsonResponse(response_data, status=200)

        except Exception as e:
            print('Exception:', str(e))
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


# WebViews
class CreateWebCheckoutSessionView(APIView):
    def post(self, request, *args, **kwargs):
        # Deserialize the incoming JSON data
        data = request.data
        product_name = data.get('name', 'Default Product Name')  # Default name if not specified
        price = data.get('price', 0)  # Default price if not specified (e.g., 20.00 EUR)
        license_plate = data.get('licensePlate', '')
        spot = data.get('spot', '')
        timestamp = data.get('timestamp', '')
        print(license_plate)

        query_params = urlencode({
            'license': license_plate,
            'spot': spot,
            'timestamp': timestamp
        })

        try:
            # Create a Stripe checkout session with dynamic price and product name
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': product_name,
                        },
                        'unit_amount': int(price * 100),  # Convert EUR to cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='http://localhost:3000/stripe/success/',
                cancel_url=f'http://localhost:3000/stripe/failure/?{query_params}',
            )
            return Response({'url': checkout_session.url}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
