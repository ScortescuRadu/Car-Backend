from django.db import models
from city.models import City

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