from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from .models import ImageTask, ParkingLot
from .serializers import ImageTaskUserInputSerializer, ImageTaskUserOutputSerializer
from user_park.models import UserPark
from django.views import View
from django.http import JsonResponse
from django.core.files.base import ContentFile
from ultralytics import YOLO
import os
import json
from io import BytesIO
from PIL import Image
# Create your views here.

class UserImageTasksView(generics.GenericAPIView):
    serializer_class = ImageTaskUserInputSerializer
    authentication_classes = [TokenAuthentication]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
         # Get the user from the token
        user_token = self.request.query_params.get('token')
        user = self.request.user if self.request.user.is_authenticated else None
        if user is None and user_token:
            try:
                user = Token.objects.get(key=user_token).user
            except Token.DoesNotExist:
                return Response({'detail': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

        # Get the parking lots associated with the user
        user_parks = UserPark.objects.filter(user=user)
        parking_lots = [user_park.parking_lot for user_park in user_parks]

        # Get the ImageTasks associated with these parking lots
        image_tasks = ImageTask.objects.filter(parking_lot__in=parking_lots)

        response_serializer = ImageTaskUserOutputSerializer(image_tasks, many=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class CreateEntranceExitView(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request, *args, **kwargs):
        serializer = ImageTaskUserInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        street_address = request.data.get('street_address')
        camera_address = request.data.get('camera_address')
        camera_type = request.data.get('camera_type')
        device_id = request.data.get('device_id')
        label = request.data.get('label')
        destination_type = request.data.get('destination_type')

        parking_lot = get_object_or_404(ParkingLot, street_address=street_address)

        # Check for existing identical entry
        existing_entry = ImageTask.objects.filter(
            parking_lot=parking_lot,
            camera_address=camera_address,
            camera_type=camera_type,
            device_id=device_id,
            label=label,
            destination_type=destination_type
        ).first()

        if existing_entry:
            return Response({
                'message': 'An identical entry already exists.',
                'id': existing_entry.id
            }, status=status.HTTP_200_OK)

        # Create new entry if no identical entry exists
        image_task = ImageTask.objects.create(
            parking_lot=parking_lot,
            camera_address=camera_address,
            camera_type=camera_type,
            device_id=device_id,
            label=label,
            destination_type=destination_type
        )

        return Response({
            'message': 'Entry created successfully',
            'id': image_task.id
        }, status=status.HTTP_201_CREATED)


model = YOLO('yolov8n.pt')

class ProcessFrameView(View):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve the frame and metadata
            frame = request.FILES.get('image_0')
            camera_address = request.POST.get('device_id_0')
            parking_lot = request.POST.get('parking_lot')  # Assuming you are sending this data

            if not frame:
                return JsonResponse({'error': 'No image file provided'}, status=400)

            # Read the image from the uploaded file
            image = Image.open(frame)

            # Convert the image to a format compatible with YOLOv8 (if necessary)
            image = image.convert('RGB')

            # Convert the image to bytes
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()

            # Perform detection
            results = model(img_byte_arr)  # Perform YOLOv8 detection
            detections = results.pandas().xyxy[0].to_json(orient="records")  # Convert detections to JSON

            # Prepare the response
            response_data = {
                'camera_address': camera_address,
                'parking_lot': parking_lot,
                'detections': json.loads(detections)
            }

            return JsonResponse(response_data, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)