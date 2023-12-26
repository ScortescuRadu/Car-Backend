from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Marker(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)