# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2021-04-11 07:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Userinfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=32, verbose_name='用户名')),
                ('mobilephone', models.CharField(max_length=16, verbose_name='手机号')),
                ('password', models.CharField(max_length=32, verbose_name='密码')),
                ('emai', models.EmailField(max_length=32, verbose_name='邮箱')),
            ],
        ),
    ]