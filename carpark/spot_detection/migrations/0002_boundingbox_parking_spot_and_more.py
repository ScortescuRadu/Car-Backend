# Generated by Django 4.2.7 on 2024-05-22 05:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parking_spot', '0001_initial'),
        ('spot_detection', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='boundingbox',
            name='parking_spot',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='parking_spot.parkingspot'),
        ),
        migrations.AlterField(
            model_name='boundingbox',
            name='bounding_boxes_json',
            field=models.JSONField(default=dict),
        ),
    ]