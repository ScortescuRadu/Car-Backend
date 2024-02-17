# Generated by Django 4.2.7 on 2024-02-12 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0002_alter_article_description_1_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='topic',
            field=models.CharField(blank=True, choices=[('sports', 'Sports'), ('announcements', 'Announcements'), ('emergency', 'Emergency'), ('city', 'City')], max_length=20, null=True),
        ),
    ]
