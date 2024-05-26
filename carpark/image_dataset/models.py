from django.db import models
from parking_lot.models import ParkingLot
# Create your models here.

class ImageDataset(models.Model):
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
    bounding_boxes_json = models.JSONField(default=dict)
    original_image_width = models.IntegerField(null=True, default=0)  # Add this line
    original_image_height = models.IntegerField(null=True, default=0) 

    def __str__(self):
        return f'Image Dataset for {self.parking_lot.street_address}'