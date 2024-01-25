from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from parking_lot.models import ParkingLot

# Create your models here.

class UserPark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s Park at {self.parking_lot}"