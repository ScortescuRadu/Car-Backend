from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

# Create your models here.

class Marker(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_subscribed = models.BooleanField(default=False)

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    marker = models.ForeignKey('Marker', on_delete=models.CASCADE)
