from celery import shared_task
import random
import base64
from celery import Celery
from carpark.celery import app
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import numpy as np
import cv2
from ultralytics import YOLO
import os

@app.task(name='tasks.add')
def add(x, y):
    return x + y


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

    image = np.frombuffer(image_data, dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    model_path = os.path.join(dir_path, 'best.pt')

    model = YOLO(model_path)
    results = model(image)
    height, width, _ = image.shape
    print('-------')
    print(height, width)
    print('-------')
    # print(results)

    xyxys = []
    confidences = []
    class_ids = []

    for result in results:
        # Convert numpy arrays to lists for serialization
        xyxys.append(result.boxes.xyxy.cpu().numpy().tolist())
        confidences.append(result.boxes.conf.cpu().numpy().tolist())
        class_ids.append(result.boxes.cls.cpu().numpy().tolist())

    # Processing complete, send bounding boxes
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "task_message",
            "message": "Processing complete",
            "content": {
                "xyxys": xyxys,
                "confidences": confidences,
                "class_ids": class_ids,
                "height": height,
                "width": width
            }
        }
    )

    return {
        "xyxys": xyxys,
        "confidences": confidences,
        "class_ids": class_ids
    }