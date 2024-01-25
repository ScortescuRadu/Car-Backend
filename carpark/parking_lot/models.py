from django.db import models

# Create your models here.

class ParkingLot(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"ParkingLot {self.id}"