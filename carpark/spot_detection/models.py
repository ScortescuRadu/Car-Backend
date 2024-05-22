from django.db import models
from parking_spot.models import ParkingSpot
from image_task.models import ImageTask
# Create your models here.

class BoundingBox(models.Model):
    image_task = models.ForeignKey(ImageTask, on_delete=models.CASCADE, default=None)
    bounding_boxes_json = models.JSONField(default=dict)
    parking_spot = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE, default=None)
    is_drawn = models.BooleanField(default=False)

    def __str__(self):
        return f'Task ID: {self.image_task.camera_address} for {self.parking_spot.level}/{self.parking_spot.sector}/{self.parking_spot.number}'