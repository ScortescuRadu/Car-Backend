from channels.generic.websocket import AsyncWebsocketConsumer
import json

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
            image_base64 = text_data_json['image']
            format, imgstr = image_base64.split(';base64,') 
            ext = format.split('/')[-1] 
            image_file = ContentFile(base64.b64decode(imgstr), name=f'{camera_address}.{ext}')
            # Save the image file to storage
            file_name = default_storage.save(f'frames/{camera_address}.{ext}', image_file)
            # Process the image or perform any additional operations here
            print(f'Received frame from camera: {camera_address}, saved to: {file_name}')
