from django.db import models
from parking_lot.models import ParkingLot
from image_task.models import ImageTask
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
# Create your models here.

class ParkingSpot(models.Model):
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE, default=None)
    image_task = models.ForeignKey(ImageTask, on_delete=models.CASCADE, null=True, default=None)
    level = models.IntegerField()
    sector = models.CharField(max_length=5)
    number = models.IntegerField()
    is_occupied = models.BooleanField()

    def __str__(self):
        return f"Spot {self.sector}{self.number} (Level {self.level}) - Lot: {self.parking_lot.street_address}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.trigger_update()

    def trigger_update(self):
        channel_layer = get_channel_layer()
        parking_lot = self.parking_lot
        image_tasks = ImageTask.objects.filter(parking_lot=parking_lot).prefetch_related('parkingspot_set')

        data = []
        for image_task in image_tasks:
            spots = ParkingSpot.objects.filter(image_task=image_task)
            task_data = {
                'camera_address': image_task.camera_address,
                'spots': list(spots.values('id', 'level', 'sector', 'number', 'is_occupied'))
            }
            data.append(task_data)

        async_to_sync(channel_layer.group_send)(
            "parking_spot_updates",
            {
                "type": "send_parking_spot_update",
                "data": {
                    "street_address": parking_lot.street_address,
                    "camera_data": data
                }
            }
        )