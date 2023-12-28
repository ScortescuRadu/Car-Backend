from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

# Create your models here.

class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class UserInfo(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='info')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    credit_card = models.CharField(max_length=16, blank=True, null=True)

    def __str__(self):
        return f"{self.user.email}'s Info"