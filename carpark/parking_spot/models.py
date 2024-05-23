from django.db import models
from parking_lot.models import ParkingLot
from image_task.models import ImageTask
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
