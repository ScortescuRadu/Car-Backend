from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from parking_lot.models import ParkingLot

# Create your models here.

class ParkingInvoice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE, default=None)
    timestamp = models.DateTimeField(default=timezone.now)
    hourly_price = models.DecimalField(max_digits=8, decimal_places=2)
    spot_description = models.CharField(max_length=255)
    time_spent = models.PositiveIntegerField(default=0)  # in hours
    is_paid = models.BooleanField(default=False)
    final_cost = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    license_plate = models.CharField(max_length=255, default="")
    reserved_time = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice for User ID: {self.user} at Parking Lot ID: {self.parking_lot}"