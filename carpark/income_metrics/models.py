from django.db import models
from parking_lot.models import ParkingLot

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