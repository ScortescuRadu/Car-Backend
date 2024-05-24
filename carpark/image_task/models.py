from django.db import models
from parking_lot.models import ParkingLot
# Create your models here.

class ImageTask(models.Model):
    CAMERA_TYPE_CHOICES = [
        ('connectedCamera', 'Connected Camera'),
        ('remoteIP', 'Remote IP Address'),
        ('liveStream', 'Live Stream'),
        ('localVideo', 'Local Video'),
    ]

    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    camera_address = models.CharField(max_length=255)
    camera_type = models.CharField(max_length=50, choices=CAMERA_TYPE_CHOICES, default=None, null=True)
    device_id = models.CharField(max_length=255, null=True, blank=True)
    label = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Image Task for {self.parking_lot.street_address} at {self.camera_address}"