# Generated by Django 4.1.13 on 2024-06-11 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('image_task', '0005_alter_imagetask_destination_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='imagetask',
            name='original_image_height',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='imagetask',
            name='original_image_width',
            field=models.IntegerField(default=0, null=True),
        ),
    ]