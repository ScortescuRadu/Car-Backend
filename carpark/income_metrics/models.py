from django.db import models
from parking_lot.models import ParkingLot
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
# Create your models here.

def default_daily_income():
    return {'Monday': 0, 'Tuesday': 0, 'Wednesday': 0, 'Thursday': 0, 'Friday': 0, 'Saturday': 0, 'Sunday': 0}

def default_monthly_income():
    # Names the months explicitly
    months = {
        'January':  0,
        'February': 0,
        'March': 0,
        'April': 0,
        'May': 0,
        'June': 0,
        'July': 0,
        'August': 0,
        'September': 0,
        'October': 0,
        'November': 0,
        'December': 0
    }
    return months

class IncomeMetrics(models.Model):
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    total_current_income = models.PositiveIntegerField(default=0)
    daily_current = models.JSONField(default=default_daily_income)
    daily_average = models.JSONField(default=default_daily_income)
    monthly_total = models.JSONField(default=default_monthly_income)
    yearly_total = models.JSONField(default=dict)
    last_update = models.DateField(auto_now=True)

    def __str__(self):
        return f"Income Metrics for {self.parking_lot.street_address}"

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
                    "total_current_income": self.total_current_income,
                    "daily_current": self.daily_current,
                    "daily_average": self.daily_average,
                    "monthly_total": self.monthly_total,
                    "yearly_total": self.yearly_total,
                    "last_update": self.last_update.isoformat(),
                    "street_address": self.parking_lot.street_address
                }
            }
        )