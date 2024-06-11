from django.shortcuts import render
import json
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .tasks import process_image_task
from .models import BoundingBox
from django.views import View
from rest_framework import generics
from django.shortcuts import get_object_or_404
from django.views import generic
from .serializers import BoundingBoxSerializer, ImageProcessSerializer, BoundingBoxInputSerializer
from parking_lot.models import ParkingLot
from image_task.models import ImageTask
from parking_spot.models import ParkingSpot
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

# Create your views here.


class ProcessImageView(generics.CreateAPIView):
    serializer_class = ImageProcessSerializer

    def create(self, request, *args, **kwargs):
        try:
            # Get the uploaded image
            image = request.FILES.get('image')

            if image:
                # Convert the image data to base64
                image_base64 = base64.b64encode(image.read()).decode('utf-8')

                # Call the Celery task for image processing
                result = process_image_task.delay(image_base64)

                # Return the task ID for the client to check the status
                return Response({'task_id': result.id}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({'error': 'Missing image'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log the exception for debugging purposes
            print(f"An unexpected error occurred: {str(e)}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckTaskStatusView(View):
    def get(self, request, task_id):
        result = process_image_task.AsyncResult(task_id)

        if result.successful():
            # Task completed successfully
            return JsonResponse({'status': 'SUCCESS', 'result': result.result})
        elif result.failed():
            # Task failed
            return JsonResponse({'status': 'FAILURE', 'message': result.traceback})
        else:
            # Task still in progress
            return JsonResponse({'status': 'PENDING'})


class StoreBoundingBoxesView(generics.CreateAPIView):
    serializer_class = BoundingBoxInputSerializer
    authentication_classes = [TokenAuthentication]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        street_address = serializer.validated_data['street_address']
        camera_address = serializer.validated_data['camera_address']
        bounding_boxes = serializer.validated_data['bounding_boxes']
        destination_type = serializer.validated_data['destination_type']
        camera_type = serializer.validated_data['camera_type']
        
        # Get the user from the token
        user_token = self.request.query_params.get('token')
        user = self.request.user if self.request.user.is_authenticated else None
        if user is None and user_token:
            try:
                user = Token.objects.get(key=user_token).user
            except Token.DoesNotExist:
                return Response({'detail': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

        # Get or create the ParkingLot
        parking_lot = get_object_or_404(ParkingLot, street_address=street_address)

        # Create or get the ImageTask
        image_task, created = ImageTask.objects.get_or_create(
            parking_lot=parking_lot,
            camera_address=camera_address,
            destination_type=destination_type,
            camera_type=camera_type
        )

        # Delete existing bounding boxes for the given camera address and parking lot
        BoundingBox.objects.filter(
            image_task__camera_address=camera_address,
            image_task__parking_lot=parking_lot
        ).delete()

        # Iterate over bounding boxes and create entries
        for box_data in bounding_boxes:
            level = box_data['level']
            sector = box_data['letter']
            number = box_data['number']
            is_drawn = box_data['is_drawn']

            # Retrieve or create the ParkingSpot
            parking_spot, created = ParkingSpot.objects.get_or_create(
                parking_lot=parking_lot,
                image_task=image_task,
                level=level,
                sector=sector,
                number=number,
                defaults={'is_occupied': False}  # Default value for is_occupied
            )

            # Create BoundingBox associated with the ParkingSpot
            BoundingBox.objects.create(
                image_task=image_task,
                bounding_boxes_json=box_data['box'],
                parking_spot=parking_spot,
                is_drawn=is_drawn
            )

        return Response({'message': 'Bounding boxes stored successfully'}, status=status.HTTP_201_CREATED)
