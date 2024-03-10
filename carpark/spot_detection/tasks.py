from celery import shared_task
import random
import base64
from celery import Celery
from carpark.celery import app

@app.task(name='tasks.add')
def add(x, y):
    return x + y

@shared_task
def process_image_task(image_base64):
    image_data = base64.b64decode(image_base64)
    # Call your image processing logic
    bounding_boxes = [1,2]
    # = process_image_logic(image)

    # Return the bounding boxes
    return bounding_boxes