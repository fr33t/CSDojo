# Generated by Django 5.1.7 on 2025-03-18 04:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('challenge', '0002_challenge_run_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='difficulty',
            field=models.IntegerField(choices=[(0, '简单'), (1, '中等'), (2, '困难'), (3, '疯狂')], default=0, verbose_name='题目难度'),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='flag_type',
            field=models.IntegerField(choices=[(0, '静态'), (1, '动态')], default=0, verbose_name='Flag类型'),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='run_type',
            field=models.IntegerField(choices=[(0, 'Dockerfile'), (1, 'DockerImage'), (2, 'URL')], default=0, verbose_name='启动文件类型'),
        ),
    ]
