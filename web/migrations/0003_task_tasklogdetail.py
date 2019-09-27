# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-09-21 11:40
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_auto_20190916_1802'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_type', models.CharField(choices=[('cmd', '批量任务'), ('file-transfer', '文件传输')], max_length=64)),
                ('content', models.CharField(max_length=255, verbose_name='任务内容')),
                ('data', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TaskLogDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.TextField(verbose_name='任务执行结果')),
                ('status', models.SmallIntegerField(choices=[(0, 'initialized'), (1, 'success'), (2, 'failed'), (3, 'timeout')], default=0)),
                ('data', models.DateTimeField(auto_now_add=True)),
                ('host_to_remote_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.HostToRemoteUser')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.Task')),
            ],
        ),
    ]
