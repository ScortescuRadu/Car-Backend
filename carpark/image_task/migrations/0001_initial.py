# Generated by Django 4.2.7 on 2024-05-22 09:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('parking_lot', '0007_alter_parkinglot_latitude_alter_parkinglot_longitude'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('camera_address', models.CharField(max_length=255)),
                ('parking_lot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parking_lot.parkinglot')),
            ],
        ),
    ]
