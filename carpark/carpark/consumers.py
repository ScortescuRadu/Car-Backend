from channels.generic.websocket import AsyncWebsocketConsumer
import json
import base64
from django.core.files.base import ContentFile
from .utils import process_image_and_extract_license_plate
from parking_lot.models import ParkingLot
from user_park.models import UserPark
from parking_invoice.models import ParkingInvoice
from user_profile.models import UserProfile
from spot_detection.models import BoundingBox
from parking_spot.models import ParkingSpot
from image_task.models import ImageTask
from spot_detection.serializers import BoundingBoxesSerializer
from ultralytics import YOLO
import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw
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

model_car = YOLO('/Users/raduscortescu/Desktop/Car-Backend/carpark/yolov8n.pt')

class SpotFrameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("spot_frame", self.channel_name)
        await self.accept()
        print("WebSocket connection opened for spot frame")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("spot_frame", self.channel_name)
        print(f"WebSocket connection closed with code: {close_code}")

    async def receive(self, text_data):
        print("Message received from WebSocket")
        try:
            data = json.loads(text_data)
            image_data = base64.b64decode(data['image'])
            camera_address = data['camera_address']
            parking_lot_address = data['parking_lot']
            camera_type = data.get('camera_type', 'localVideo')  # Default to 'localVideo' if not provided
            token = data['token']

            print(f"Received data: camera_address={camera_address}, parking_lot_address={parking_lot_address}, camera_type={camera_type}")

            # Retrieve the image task
            image_task = await self.get_image_task(parking_lot_address, camera_address, camera_type)
            if not image_task:
                await self.send(text_data=json.dumps({'detail': 'Image task not found'}))
                print("Image task not found")
                return

            print(f"Found image task: {image_task}")

            # Fetch bounding boxes for the image task
            bounding_boxes = await self.get_bounding_boxes(image_task)
            print(f"Found bounding boxes: {bounding_boxes}")

            image_np = self.convert_image_data_to_np(image_data)
            print(f"Converted image to numpy array: shape={image_np.shape}")

            results = model_car(image_np)
            object_counts, summary_string = self.process_detections(results)
            print(f"Processed detections: {summary_string}")

            # Check overlap and update bounding boxes
            updated_bounding_boxes = self.check_and_update_bounding_boxes(bounding_boxes, results)

            # Save the image with bounding boxes
            self.save_image_with_boxes(image_np, updated_bounding_boxes, results)

            response_data = {
                'camera_address': camera_address,
                'parking_lot': parking_lot_address,
                'summary_string': summary_string,
                'bounding_boxes': updated_bounding_boxes
            }

            await self.send(text_data=json.dumps(response_data))
            print(f"Sent response data: {response_data}")

        except Exception as e:
            print(f"Error processing WebSocket message: {str(e)}")

    @sync_to_async
    def get_image_task(self, parking_lot_address, camera_address, camera_type):
        try:
            print(f"Fetching parking lot: {parking_lot_address}")
            parking_lot = ParkingLot.objects.filter(street_address=parking_lot_address).first()
            if not parking_lot:
                print("Parking lot not found")
                return None

            print(f"Fetching image task for parking_lot={parking_lot}, camera_address={camera_address}, camera_type={camera_type}")
            image_task = ImageTask.objects.filter(parking_lot=parking_lot,
                                                  camera_address=camera_address,
                                                  camera_type=camera_type).first()
            if image_task:
                print(f"Image task details: {image_task}")
            else:
                print(f"No image task found with parking_lot={parking_lot}, camera_address={camera_address}, camera_type={camera_type}")
            return image_task
        except Exception as e:
            print(f"Error retrieving image task: {str(e)}")
            return None

    @sync_to_async
    def get_bounding_boxes(self, image_task):
        try:
            print(f"Fetching bounding boxes for image_task={image_task}")
            bounding_boxes = BoundingBox.objects.filter(image_task=image_task)
            bounding_boxes_data = BoundingBoxesSerializer(bounding_boxes, many=True).data
            return bounding_boxes_data
        except Exception as e:
            print(f"Error retrieving bounding boxes: {str(e)}")
            return []

    def convert_image_data_to_np(self, image_data):
        import cv2
        image = Image.open(BytesIO(image_data))
        image = image.convert('RGB')
        image_np = np.array(image)
        image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        return image_np

    def process_detections(self, results):
        object_counts = {
            "car": 0,
            "bus": 0,
            "truck": 0
        }
        for result in results:
            for box in result.boxes:
                cls = int(box.cls.cpu().numpy())
                class_name = model_car.names[cls] if cls in model_car.names else 'unknown'

                if class_name in object_counts:
                    object_counts[class_name] += 1

        summary_string = f"{object_counts['car']} cars, {object_counts['bus']} buses, {object_counts['truck']} trucks"
        return object_counts, summary_string

    def check_and_update_bounding_boxes(self, bounding_boxes, results):
        def calculate_iou(box1, box2):
            x1_max = max(box1[0], box2[0])
            y1_max = max(box1[1], box2[1])
            x2_min = min(box1[2], box2[2])
            y2_min = min(box1[3], box2[3])

            inter_area = max(0, x2_min - x1_max) * max(0, y2_min - y1_max)

            box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
            box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])

            iou = inter_area / float(box1_area + box2_area - inter_area)
            return iou

        updated_bounding_boxes = []
        iou_threshold = 0.2

        for spot in bounding_boxes:
            spot_box = [
                spot['bounding_boxes_json'][0],
                spot['bounding_boxes_json'][1],
                spot['bounding_boxes_json'][2],
                spot['bounding_boxes_json'][3]
            ]
            spot['is_empty'] = True

            for result in results:
                for box in result.boxes:
                    cls = int(box.cls.cpu().numpy())
                    class_name = model_car.names[cls] if cls in model_car.names else 'unknown'
                    if class_name == 'car':
                        car_box = box.xyxy[0].cpu().numpy().tolist()
                        iou = calculate_iou(spot_box, car_box)
                        if iou > iou_threshold:  # Threshold for considering the spot as occupied
                            spot['is_empty'] = False
                            break
                if not spot['is_empty']:
                    break

            updated_bounding_boxes.append(spot)

        return updated_bounding_boxes

    def save_image_with_boxes(self, image_np, bounding_boxes, results):
        # Convert the image to RGB (cv2 loads it as BGR by default)
        image = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        
        # Draw spot bounding boxes
        for spot in bounding_boxes:
            spot_box = [
                int(spot['bounding_boxes_json'][0]),
                int(spot['bounding_boxes_json'][1]),
                int(spot['bounding_boxes_json'][2]),
                int(spot['bounding_boxes_json'][3])
            ]
            color = (0, 255, 0) if spot['is_empty'] else (0, 0, 255)  # Green if empty, red if occupied
            cv2.rectangle(image, (spot_box[0], spot_box[1]), (spot_box[2], spot_box[3]), color, 2)

        # Draw car bounding boxes
        for result in results:
            for box in result.boxes:
                car_box = box.xyxy[0].cpu().numpy().astype(int).tolist()
                cv2.rectangle(image, (car_box[0], car_box[1]), (car_box[2], car_box[3]), (255, 0, 0), 2)  # Blue for cars

        # Save the image with bounding boxes locally for debugging
        debug_image_path = os.path.join('debug_images', 'debug_image_with_boxes.jpg')
        os.makedirs(os.path.dirname(debug_image_path), exist_ok=True)  # Ensure the directory exists
        cv2.imwrite(debug_image_path, image)
        print(f'Debug image with bounding boxes saved at: {debug_image_path}')
