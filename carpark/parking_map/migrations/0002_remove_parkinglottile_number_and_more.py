# Generated by Django 4.2.7 on 2024-05-15 06:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parking_lot', '0007_alter_parkinglot_latitude_alter_parkinglot_longitude'),
        ('parking_map', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parkinglottile',
            name='number',
        ),
        migrations.RemoveField(
            model_name='parkinglottile',
            name='position',
        ),
        migrations.RemoveField(
            model_name='parkinglottile',
            name='rotation',
        ),
        migrations.RemoveField(
            model_name='parkinglottile',
            name='sector',
        ),
        migrations.RemoveField(
            model_name='parkinglottile',
            name='tile_type',
        ),
        migrations.AddField(
            model_name='parkinglottile',
            name='tiles_data',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='parkinglottile',
            name='parking_lot',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='tiles', to='parking_lot.parkinglot'),
        ),
    ]