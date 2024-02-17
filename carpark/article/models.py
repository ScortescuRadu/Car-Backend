from django.db import models

# Create your models here.
class Article(models.Model):
    cover = models.ImageField(upload_to = 'img', blank=True, null=True)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=400)

    cover_section_1 = models.ImageField(upload_to = 'img', blank=True, null=True)
    subtitle_1 = models.CharField(max_length=200, blank=True, null=True)
    description_1 = models.CharField(max_length=400, blank=True, null=True)

    cover_section_2 = models.ImageField(upload_to = 'img', blank=True, null=True)
    subtitle_2 = models.CharField(max_length=200, blank=True, null=True)
    description_2 = models.CharField(max_length=400, blank=True, null=True)

    timestamp = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)

    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    TOPIC_CHOICES = [
        ('sports', 'Sports'),
        ('announcements', 'Announcements'),
        ('emergency', 'Emergency'),
        ('city', 'City'),
    ]
    topic = models.CharField(max_length=20, choices=TOPIC_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.title
