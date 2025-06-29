# Generated by Django 5.1.7 on 2025-03-17 12:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=3000, verbose_name='题目标题')),
                ('description', models.CharField(max_length=3000, verbose_name='题目描述')),
                ('author', models.CharField(max_length=200, verbose_name='作者')),
                ('related_url', models.CharField(max_length=300, verbose_name='相关链接')),
                ('visibility', models.BooleanField(default=False, verbose_name='可见性')),
                ('created_at', models.DateField(verbose_name='添加日期')),
                ('run_type', models.IntegerField(choices=[(0, 'Dockerfile'), (1, 'DockerImage'), (2, 'URL')], verbose_name='启动文件类型')),
                ('flag_type', models.IntegerField(choices=[(0, 'STATIC'), (1, 'DYNAMIC')], verbose_name='Flag类型')),
                ('categories', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='challenge.category', verbose_name='类别')),
                ('tags', models.ManyToManyField(blank=True, to='challenge.tag', verbose_name='标签')),
            ],
        ),
    ]
