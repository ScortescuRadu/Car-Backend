# Generated by Django 4.2.7 on 2023-12-28 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cover', models.ImageField(blank=True, null=True, upload_to='img')),
                ('title', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=400)),
                ('cover_section_1', models.ImageField(blank=True, null=True, upload_to='img')),
                ('subtitle_1', models.CharField(max_length=200, null=True)),
                ('description_1', models.CharField(max_length=400, null=True)),
                ('cover_section_2', models.ImageField(blank=True, null=True, upload_to='img')),
                ('subtitle_2', models.CharField(max_length=200, null=True)),
                ('description_2', models.CharField(max_length=400, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
            ],
        ),
    ]
