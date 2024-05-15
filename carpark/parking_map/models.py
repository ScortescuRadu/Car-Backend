from django.db import models
from parking_lot.models import ParkingLot
# Create your models here.

class ParkingLotTile(models.Model):
    parking_lot = models.OneToOneField(ParkingLot, on_delete=models.CASCADE, related_name='tiles')
    tiles_data = models.JSONField(default=dict)  # Use JSON field to store tile data

    def __str__(self):
        return f"Tiles for {self.parking_lot.street_address}"
