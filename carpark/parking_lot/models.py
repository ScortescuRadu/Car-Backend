from django.db import models

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
    street_address = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"ParkingLot {self.id}"