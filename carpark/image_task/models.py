from django.db import models
from parking_lot.models import ParkingLot
# Create your models here.

class ImageTask(models.Model):
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    camera_address = models.CharField(max_length=255)

    def __str__(self):
        return f"Image Task for {self.parking_lot.street_address} at {self.camera_address}"