from django.db import models
from django.conf import settings
from parking_lot.models import ParkingLot
from entrance.models import Entrance

# Create your models here.

class ParkingEntrance(models.Model):
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    entrance = models.ForeignKey(Entrance, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.parking_lot}'s entrance:  {self.entrance}"