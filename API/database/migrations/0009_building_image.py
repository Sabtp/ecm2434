# Generated by Django 4.1.6 on 2023-02-27 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0008_achievement_name_alter_user_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='building',
            name='image',
            field=models.ImageField(blank=True, upload_to=''),
        ),
    ]