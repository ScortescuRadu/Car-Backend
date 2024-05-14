from django.db import models
from city.models import City
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
# Create your models here.

class ParkingLot(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField()
    iban = models.CharField(max_length=34, null=True, blank=True)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    weekday_opening_time = models.TimeField(null=True, blank=True)
    weekday_closing_time = models.TimeField(null=True, blank=True)
    weekend_opening_time = models.TimeField(null=True, blank=True)
    weekend_closing_time = models.TimeField(null=True, blank=True)
    street_address = models.CharField(max_length=255, unique=True, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    latitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)

    def __str__(self):
        return f"ParkingLot {self.street_address}"

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
                    "id": self.id,
                    "price": str(self.price),
                    "capacity": self.capacity,
                    "phone_number": self.phone_number,
                    "weekday_opening_time": self.weekday_opening_time.isoformat() if self.weekday_opening_time else None,
                    "weekday_closing_time": self.weekday_closing_time.isoformat() if self.weekday_closing_time else None,
                    "weekend_opening_time": self.weekend_opening_time.isoformat() if self.weekend_opening_time else None,
                    "weekend_closing_time": self.weekend_closing_time.isoformat() if self.weekend_closing_time else None,
                    "street_address": self.street_address,
                    "latitude": str(self.latitude) if self.latitude else None,
                    "longitude": str(self.longitude) if self.longitude else None,
                }
            }
        )