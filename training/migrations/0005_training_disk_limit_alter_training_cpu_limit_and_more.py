# Generated by Django 5.1.7 on 2025-03-19 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0004_training_cpu_limit_training_memory_limit'),
    ]

    operations = [
        migrations.AddField(
            model_name='training',
            name='disk_limit',
            field=models.PositiveIntegerField(default=256, verbose_name='磁盘空间'),
        ),
        migrations.AlterField(
            model_name='training',
            name='cpu_limit',
            field=models.PositiveIntegerField(blank=True, default=1, null=True, verbose_name='CPU核数'),
        ),
        migrations.AlterField(
            model_name='training',
            name='memory_limit',
            field=models.PositiveIntegerField(blank=True, default=64, null=True, verbose_name='分配内存'),
        ),
    ]
