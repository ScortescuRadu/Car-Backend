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

    DESTINATION_TYPE_CHOICES = [
        ('spot', 'Spot'),
        ('entrance', 'Entrance'),
        ('exit', 'Exit'),
    ]

    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    camera_address = models.CharField(max_length=255)
    camera_type = models.CharField(max_length=50, choices=CAMERA_TYPE_CHOICES, default=None, null=True)
    device_id = models.CharField(max_length=255, null=True, blank=True)
    label = models.CharField(max_length=255, null=True, blank=True)
    destination_type = models.CharField(max_length=50, choices=DESTINATION_TYPE_CHOICES, default='spot', null=True)
    original_image_width = models.IntegerField(null=True, default=0)
    original_image_height = models.IntegerField(null=True, default=0)

    def __str__(self):
        return f"Image Task {self.destination_type} for {self.parking_lot.street_address} at {self.camera_address}"