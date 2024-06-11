from channels.generic.websocket import AsyncWebsocketConsumer
import json
import base64
from django.core.files.base import ContentFile
from .utils import process_image_and_extract_license_plate
from user_park.models import UserPark
from parking_invoice.models import ParkingInvoice
from user_profile.models import UserProfile
from ultralytics import YOLO
import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import logging
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from io import BytesIO
from easyocr import Reader
from datetime import timedelta
from django.utils import timezone
from asgiref.sync import sync_to_async

class TaskStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        await self.channel_layer.group_add(
            f"task_{self.task_id}",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            f"task_{self.task_id}",
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(
            f"task_{self.task_id}",
            {
                'type': message_type,
                'message': message,
            }
        )

    async def task_message(self, event):
        message = event['message']
        content = event.get('content', [])

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'content': content
        }))


class ParkingLotUpdateDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("parking_lot_updates", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("parking_lot_updates", self.channel_name)

    async def receive(self, text_data):
        pass

    async def send_parking_lot_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))


class ParkingSpotUpdateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("parking_spot_updates", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("parking_spot_updates", self.channel_name)

    async def receive(self, text_data):
        pass

    async def send_parking_spot_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))


class CameraUpdateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("camera_updates", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("camera_updates", self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'frame_data':
            camera_address = text_data_json['camera_address']
            destination_type = text_data_json['destination_type']
            image_base64 = text_data_json['image']
            format, imgstr = image_base64.split(';base64,') 
            image_data = base64.b64decode(imgstr)
            image_file = ContentFile(image_data, name=f'{camera_address}.jpg')

            # Process the image to extract the license plate
            license_plate = process_image_and_extract_license_plate(image_file)

            # Log the result or perform any additional operations here
            print(f'Received frame from camera: {camera_address}, license plate: {license_plate}, destination: {destination_type}')


model_license_plate = YOLO('/Users/raduscortescu/Desktop/Car-Backend/carpark/image_task/license_plate_detector.pt')
reader = Reader(['en'])

class EntranceExitFrameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("entrance_exit_frame", self.channel_name)
        await self.accept()
        print("WebSocket connection opened")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("entrance_exit_frame", self.channel_name)
        print(f"WebSocket connection closed with code: {close_code}")

    async def receive(self, text_data):
        print("Message received from WebSocket")
        try:
            data = json.loads(text_data)
            image_data = base64.b64decode(data['image'])
            camera_address = data['device_id_0']
            parking_lot_address = data['parking_lot']
            token = data['token']

            image_np = self.convert_image_data_to_np(image_data)

            results = model_license_plate(image_np)
            ocr_texts = self.process_detections(results, image_np, token, parking_lot_address)

            response_data = {
                'camera_address': camera_address,
                'parking_lot': parking_lot_address,
                'ocr_texts': ocr_texts
            }

            await self.send(text_data=json.dumps(response_data))
            print(f"Sent response data: {response_data}")

        except Exception as e:
            print(f"Error processing WebSocket message: {str(e)}")

    def convert_image_data_to_np(self, image_data):
        import cv2
        image = Image.open(BytesIO(image_data))
        image = image.convert('RGB')
        image_np = np.array(image)
        image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        return image_np

    def process_detections(self, results, image_np, token, parking_lot_address):
        ocr_texts = []
        for result in results:
            for box in result.boxes:
                bbox = box.xyxy[0].cpu().numpy().tolist()
                conf = float(box.conf.cpu().numpy())
                cls = int(box.cls.cpu().numpy())
                class_name = model_license_plate.names[cls] if cls in model_license_plate.names else 'unknown'

                if class_name == "license_plate":
                    license_plate_img = image_np[int(bbox[1]):int(bbox[3]), int(bbox[0]):int(bbox[2])]
                    ocr_text = self.perform_ocr(license_plate_img)
                    ocr_texts.append(ocr_text)

                    self.create_invoice_if_needed(ocr_text, token, parking_lot_address)

        return ocr_texts

    def perform_ocr(self, license_plate_img):
        try:
            ocr_results = reader.readtext(license_plate_img)
            if ocr_results:
                print(f"OCR results: {ocr_results}")
                return ocr_results[0][1]
        except Exception as e:
            print(f"Error during OCR: {str(e)}")
        return ''

    @sync_to_async
    def create_invoice_if_needed(self, ocr_text, token, parking_lot_address):
        from django.conf import settings

        try:
            if ocr_text:
                recent_time = timezone.now() - timedelta(minutes=2)
                existing_invoices = ParkingInvoice.objects.filter(
                    license_plate=ocr_text,
                    timestamp__gte=recent_time
                )

                if not existing_invoices.exists():
                    user = None
                    if token:
                        try:
                            user = Token.objects.get(key=token).user
                        except Token.DoesNotExist:
                            print("Token does not exist")

                    if not user:
                        try:
                            user_profile = UserProfile.objects.get(car_id=ocr_text)
                            user = user_profile.user
                        except UserProfile.DoesNotExist:
                            user = settings.AUTH_USER_MODEL.objects.first()  # Default user

                    parking_lot = get_object_or_404(ParkingLot, street_address=parking_lot_address)
                    ParkingInvoice.objects.create(
                        user=user,
                        parking_lot=parking_lot,
                        hourly_price=parking_lot.price,
                        spot_description='Example spot',
                        time_spent=1,
                        final_cost=parking_lot.price,
                        license_plate=ocr_text
                    )
                    print(f"Created new invoice for license plate: {ocr_text}")

        except Exception as e:
            print(f"Error creating invoice: {str(e)}")