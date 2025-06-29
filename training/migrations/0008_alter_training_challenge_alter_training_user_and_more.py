# Generated by Django 5.1.7 on 2025-03-20 06:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_rename_password_user_password_hash'),
        ('challenge', '0012_alter_challenge_category_alter_challenge_tags'),
        ('training', '0007_alter_training_created_at_alter_training_started_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='training',
            name='challenge',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trainings', to='challenge.challenge', verbose_name='题目'),
        ),
        migrations.AlterField(
            model_name='training',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trainings', to='account.user', verbose_name='谁开启的题目'),
        ),
        migrations.AlterField(
            model_name='traininglog',
            name='training',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='training_logs', to='training.training'),
        ),
        migrations.AlterField(
            model_name='traininglog',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='training_logs', to='account.user'),
        ),
    ]
