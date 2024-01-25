from django.db import models

# Create your models here.

class OperatingHours(models.Model):
    DAY_CHOICES = [
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ]

    day = models.CharField(max_length=3, choices=DAY_CHOICES, null=False, blank=False)
    opening_time = models.TimeField(null=False, blank=False)
    closing_time = models.TimeField(null=False, blank=False)

    class Meta:
        unique_together = ('day', 'opening_time', 'closing_time')

    def __str__(self):
        return f"{self.get_day_display()}: {self.opening_time} - {self.closing_time}"
