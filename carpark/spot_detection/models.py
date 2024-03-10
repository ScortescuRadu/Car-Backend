from django.db import models

# Create your models here.

class BoundingBox(models.Model):
    task_id = models.CharField(max_length=255)
    bounding_boxes_json = models.TextField()

    def __str__(self):
        return f'Task ID: {self.task_id}'