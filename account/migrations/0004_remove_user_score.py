# Generated by Django 5.1.7 on 2025-03-21 03:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_user_score'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='score',
        ),
    ]
