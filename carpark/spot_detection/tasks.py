from celery import shared_task
import random
import base64
from celery import Celery
from carpark.celery import app
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@app.task(name='tasks.add')
def add(x, y):
    return x + y

# using websockets
@shared_task
def process_image_task(image_base64):
    image_data = base64.b64decode(image_base64)
    channel_layer = get_channel_layer()
    task_id = process_image_task.request.id  # Celery task ID
    group_name = f'task_{task_id}'

    # Simulate some processing and send updates
    async_to_sync(channel_layer.group_send)(
        group_name,
        {"type": "task_message", "message": "Processing started"}
    )

    # Processing complete, send bounding boxes
    content = [{"x": 10, "y": 20, "width": 100, "height": 200}]
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "task_message",
            "message": "Processing complete",
            "content": content
        }
    )

    return content