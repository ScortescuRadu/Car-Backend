from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class ParkingInvoice(models.Model):
    user_id = models.PositiveIntegerField()
    parking_lot_id = models.PositiveIntegerField()
    timestamp = models.DateTimeField(default=timezone.now)
    hourly_price = models.DecimalField(max_digits=8, decimal_places=2)
    spot_description = models.CharField(max_length=255)
    time_spent = models.PositiveIntegerField(default=0)  # in hours
    is_paid = models.BooleanField(default=False)
    final_cost = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    license_plate = models.CharField(max_length=255, default="")
    reserved_time = models.PositiveIntegerField(default=0)  # in hours

    def __str__(self):
        return f"Invoice for User ID: {self.user_id} at Parking Lot ID: {self.parking_lot_id}"