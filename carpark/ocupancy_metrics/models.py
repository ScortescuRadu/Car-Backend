from django.db import models
from parking_lot.models import ParkingLot
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
# Create your models here.

def default_week_structure():
    hours = {f"{i:02d}:00": 0 for i in range(24)}
    return {
        'Monday': hours.copy(), 'Tuesday': hours.copy(), 'Wednesday': hours.copy(),
        'Thursday': hours.copy(), 'Friday': hours.copy(),
        'Saturday': hours.copy(), 'Sunday': hours.copy()
    }

class OccupancyMetrics(models.Model):
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    total_current_occupancy = models.PositiveIntegerField(default=0)
    current_occupancy = models.JSONField(default=default_week_structure)
    average_occupancy = models.JSONField(default=default_week_structure)
    last_update = models.DateField(auto_now=True)

    def __str__(self):
        return f"Occupancy Metrics for {self.parking_lot.street_address}"

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
                    "total_current_occupancy": self.total_current_occupancy,
                    "current_occupancy": self.current_occupancy,
                    "average_occupancy": self.average_occupancy,
                    "last_update": self.last_update.isoformat(),
                    "street_address": self.parking_lot.street_address
                }
            }
        )