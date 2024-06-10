from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from .models import ImageTask, ParkingLot
from .serializers import ImageTaskUserInputSerializer, ImageTaskUserOutputSerializer, FrameInputSerializer, FrameOutputSerializer, FrameOutputOCRSerializer
from user_park.models import UserPark
from django.views import View
from django.http import JsonResponse
from django.core.files.base import ContentFile
from ultralytics import YOLO
import os
import json
from io import BytesIO
from PIL import Image, ImageEnhance
import logging
import cv2
import numpy as np
from easyocr import Reader
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

            # Enhance the image brightness for debugging purposes
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.5)  # Increase brightness by 1.5x

            # Convert the image to a numpy array using cv2
            image_np = np.array(image.convert('RGB'))
            image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
            logging.info(f'Image converted to numpy array, shape: {image_np.shape}')

            # Ensure the image data type and range are correct
            if image_np.dtype != np.uint8:
                image_np = cv2.convertScaleAbs(image_np, alpha=(255.0/np.max(image_np)))
                logging.info('Image data type and range corrected')

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
                    class_name = model.names[cls]
                    detections_list.append({
                        'xmin': bbox[0],
                        'ymin': bbox[1],
                        'xmax': bbox[2],
                        'ymax': bbox[3],
                        'confidence': conf,
                        'class_name': class_name
                    })

                    # Draw bounding box on the image
                    cv2.rectangle(image_np, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (0, 255, 0), 2)
                    cv2.putText(image_np, f'{class_name} {conf:.2f}', (int(bbox[0]), int(bbox[1]) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # Save the image with bounding boxes locally for debugging
            debug_image_path = os.path.join('debug_images', 'debug_image_with_boxes.jpg')
            os.makedirs(os.path.dirname(debug_image_path), exist_ok=True)
            cv2.imwrite(debug_image_path, image_np)
            logging.info(f'Debug image with bounding boxes saved at: {debug_image_path}')

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


model_license_plate = YOLO('/Users/raduscortescu/Desktop/Car-Backend/carpark/image_task/license_plate_detector.pt')
reader = Reader(['en'], gpu=False)

class ProcessEntranceExitView(generics.GenericAPIView):
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

            # Enhance the image brightness for debugging purposes
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.5)  # Increase brightness by 1.5x

            # Convert the image to a numpy array using cv2
            image_np = np.array(image.convert('RGB'))
            image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
            logging.info(f'Image converted to numpy array, shape: {image_np.shape}')

            # Ensure the image data type and range are correct
            if image_np.dtype != np.uint8:
                image_np = cv2.convertScaleAbs(image_np, alpha=(255.0/np.max(image_np)))
                logging.info('Image data type and range corrected')

            # Perform license plate detection
            try:
                results = model_license_plate(image_np)
            except Exception as e:
                logging.error(f'Error during YOLO detection: {str(e)}')
                return Response({'error': 'YOLO detection error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            detections_list = []
            for result in results:
                if len(result.boxes) == 0:
                    logging.warning('No boxes detected in the result')
                    continue

                for box in result.boxes:
                    if len(box.xyxy) == 0:
                        logging.warning('No coordinates found in the detected box')
                        continue

                    bbox = box.xyxy[0].cpu().numpy().tolist()  # Convert to list of float
                    conf = float(box.conf.cpu().numpy())  # Convert to standard float
                    cls = int(box.cls.cpu().numpy())  # Convert to standard int
                    class_name = model_license_plate.names[cls] if cls in model_license_plate.names else 'unknown'

                    detection = {
                        'xmin': bbox[0],
                        'ymin': bbox[1],
                        'xmax': bbox[2],
                        'ymax': bbox[3],
                        'confidence': conf,
                        'class_name': class_name,
                        'ocr_text': ''  # Initialize as empty string
                    }

                    # Draw bounding box on the image
                    cv2.rectangle(image_np, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (0, 255, 0), 2)
                    cv2.putText(image_np, f'{class_name} {conf:.2f}', (int(bbox[0]), int(bbox[1]) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                    # Extract license plate region and perform OCR
                    license_plate_img = image_np[int(bbox[1]):int(bbox[3]), int(bbox[0]):int(bbox[2])]
                    try:
                        ocr_results = reader.readtext(license_plate_img)
                        for ocr_result in ocr_results:
                            detection['ocr_text'] = ocr_result[1]
                    except Exception as e:
                        logging.error(f'Error during OCR: {str(e)}')

                    detections_list.append(detection)

            # Save the image with bounding boxes locally for debugging
            debug_image_path = os.path.join('debug_images', 'debug_image_with_boxes.jpg')
            os.makedirs(os.path.dirname(debug_image_path), exist_ok=True)
            cv2.imwrite(debug_image_path, image_np)
            logging.info(f'Debug image with bounding boxes saved at: {debug_image_path}')

            detections_json = json.dumps(detections_list)
            logging.info(f'Detections: {detections_json}')

            # Prepare the response
            response_data = {
                'camera_address': camera_address,
                'parking_lot': parking_lot,
                'detections': detections_list
            }

            response_serializer = FrameOutputOCRSerializer(data=response_data)
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