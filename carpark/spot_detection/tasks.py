from celery import shared_task
import random
from celery import Celery
from carpark.celery import app

@app.task(name='tasks.add')
def add(x, y):
    return x + y