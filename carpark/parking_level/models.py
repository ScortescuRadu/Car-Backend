from django.db import models
from parking_lot.models import ParkingLot
# Create your models here.

class ParkingLevel(models.Model):
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    level = models.CharField(max_length=10)
    spots_data = jsonfield.JSONField()

    def __str__(self):
        return f"{self.parking_lot.street_address} - Level {self.level}"
