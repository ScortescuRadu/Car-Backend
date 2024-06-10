from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from .models import ImageTask, ParkingLot
from .serializers import ImageTaskUserInputSerializer, ImageTaskUserOutputSerializer, FrameInputSerializer, FrameOutputSerializer
from user_park.models import UserPark
from django.views import View
from django.http import JsonResponse
from django.core.files.base import ContentFile
from ultralytics import YOLO
import os
import json
from io import BytesIO
from PIL import Image
import logging
import cv2
import numpy as np
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

class ProcessFrameView(generics.GenericAPIView):
    serializer_class = FrameInputSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # Retrieve the frame and metadata
            frame = request.FILES.get('image_0')
            camera_address = request.POST.get('device_id_0')
            parking_lot = request.POST.get('parking_lot')

            if not frame:
                logging.error('No image file provided')
                return Response({'error': 'No image file provided'}, status=status.HTTP_400_BAD_REQUEST)

            # Read the image from the uploaded file
            try:
                image = Image.open(frame)
            except Exception as e:
                logging.error(f'Error opening image: {str(e)}')
                return Response({'error': 'Invalid image file'}, status=status.HTTP_400_BAD_REQUEST)

            logging.info(f'Original image format: {image.format}, size: {image.size}')

            # Convert the image to a numpy array using cv2
            image_np = np.array(image.convert('RGB'))
            image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
            logging.info(f'Image converted to numpy array, shape: {image_np.shape}')

            # Perform detection
            try:
                results = model(image_np)  # Perform YOLOv8 detection
            except Exception as e:
                logging.error(f'Error during YOLO detection: {str(e)}')
                return Response({'error': 'YOLO detection error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            detections_list = []
            for result in results:
                for box in result.boxes:
                    bbox = box.xyxy[0].cpu().numpy().tolist()  # Convert to list of float
                    conf = float(box.conf.cpu().numpy())  # Convert to standard float
                    cls = int(box.cls.cpu().numpy())  # Convert to standard int
                    detections_list.append({
                        'xmin': bbox[0],
                        'ymin': bbox[1],
                        'xmax': bbox[2],
                        'ymax': bbox[3],
                        'confidence': conf,
                        'class_name': model.names[cls]
                    })

            detections_json = json.dumps(detections_list)
            logging.info(f'Detections: {detections_json}')

            # Prepare the response
            response_data = {
                'camera_address': camera_address,
                'parking_lot': parking_lot,
                'detections': detections_list
            }

            response_serializer = FrameOutputSerializer(data=response_data)
            if response_serializer.is_valid():
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            else:
                logging.error(f'Serializer errors: {response_serializer.errors}')
                return Response(response_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except UnicodeDecodeError as e:
            logging.error(f'Unicode decoding error: {str(e)}')
            return Response({'error': f'Unicode decoding error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logging.error(f'General error: {str(e)}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
