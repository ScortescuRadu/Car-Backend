# Generated by Django 4.1.13 on 2024-06-21 08:50

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('parking_lot', '0007_alter_parkinglot_latitude_alter_parkinglot_longitude'),
        ('image_task', '0006_imagetask_original_image_height_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParkEntrance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('license_plate', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('image_task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='image_task.imagetask')),
                ('parking_lot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parking_lot.parkinglot')),
            ],
        ),
    ]
