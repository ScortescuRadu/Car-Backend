from django.db import models
from parking_lot.models import ParkingLot
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