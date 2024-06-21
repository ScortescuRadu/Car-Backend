from django.db import models
from django.utils import timezone
from parking_lot.models import ParkingLot
from image_task.models import ImageTask
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# Create your models here.
class ParkingExit(models.Model):
    license_plate = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    image_task = models.ForeignKey(ImageTask, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.license_plate} - {self.timestamp}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.trigger_update()

    def trigger_update(self):
        channel_layer = get_channel_layer()
        message = {
            'type': 'exit',
            'license_plate': self.license_plate,
            'timestamp': self.timestamp.isoformat(),
            'camera_address': self.image_task.camera_address,
            'is_paid': self.is_paid,
        }
        async_to_sync(channel_layer.group_send)(
            'license_plates_group',
            {
                'type': 'license_plate_message',
                'message': message
            }
        )