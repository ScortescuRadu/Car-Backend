from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from parking_lot.models import ParkingLot
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
# Create your models here.

class ParkingInvoice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, default=None)
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
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.trigger_update()

    def trigger_update(self):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "parking_lot_updates",
            {
                "type": "send_parking_lot_update",
                "data": {
                    "type": "invoice_update",
                    "id": self.id,
                    "user_id": self.user.id,
                    "parking_lot_id": self.parking_lot.id,
                    "timestamp": self.timestamp.isoformat(),
                    "hourly_price": str(self.hourly_price),
                    "spot_description": self.spot_description,
                    "time_spent": self.time_spent,
                    "is_paid": self.is_paid,
                    "final_cost": str(self.final_cost),
                    "license_plate": self.license_plate,
                    "reserved_time": self.reserved_time,
                    "street_address": self.parking_lot.street_address
                }
            }
        )