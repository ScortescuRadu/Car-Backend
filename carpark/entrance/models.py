from django.db import models

# Create your models here.

class Entrance(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"Entrance at ({self.latitude}, {self.longitude})"