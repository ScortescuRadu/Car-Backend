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
