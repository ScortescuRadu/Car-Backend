from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.

class UserStripe(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Park at {self.stripe}"