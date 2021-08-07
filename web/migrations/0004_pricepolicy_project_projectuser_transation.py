# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2021-04-14 10:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_auto_20210412_0105'),
    ]

    operations = [
        migrations.CreateModel(
            name='PricePolicy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.SmallIntegerField(choices=[(3, '其他'), (1, '免费版'), (2, '收费版')], default=2, verbose_name='收费类型')),
                ('title', models.CharField(max_length=32, verbose_name='标题')),
                ('price', models.CharField(max_length=32, verbose_name='价格')),
                ('project_num', models.PositiveIntegerField(verbose_name='项目数')),
                ('project_member', models.PositiveIntegerField(verbose_name='项目成员数')),
                ('project_space', models.PositiveIntegerField(verbose_name='项目空间')),
                ('per_file_size', models.PositiveIntegerField(verbose_name='单文件上传大小（M）')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='项目名')),
                ('color', models.SmallIntegerField(choices=[(6, '#11EEEE'), (1, '#F70909'), (7, '#96EE11'), (3, '#11EE11'), (5, '#C211EE'), (2, '#EEEE11'), (4, '#113DEE')], default=1, verbose_name='颜色')),
                ('desc', models.CharField(blank=True, max_length=512, null=True, verbose_name='项目描述')),
                ('use_space', models.IntegerField(default=0, verbose_name='项目已使用空间')),
                ('star', models.BooleanField(default=False, verbose_name='星标')),
                ('join_count', models.SmallIntegerField(default=1, verbose_name='参与人数')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.Userinfo', verbose_name='项目创建者')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('star', models.BooleanField(default=False, verbose_name='星标')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='加入时间')),
                ('invitor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invitor', to='web.Userinfo', verbose_name='邀请人')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.Project', verbose_name='项目')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to='web.Userinfo', verbose_name='用户')),
            ],
        ),
        migrations.CreateModel(
            name='Transation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.SmallIntegerField(choices=[(0, '未支付'), (1, '已支付')], verbose_name='状态')),
                ('order', models.CharField(max_length=64, unique=True, verbose_name='订单号')),
                ('count', models.IntegerField(help_text='0表示无限期', verbose_name='数量（年）')),
                ('price', models.IntegerField(verbose_name='实际支付价格')),
                ('start_time', models.DateTimeField(blank=True, null=True, verbose_name='开始时间')),
                ('end_time', models.DateTimeField(blank=True, null=True, verbose_name='结束时间')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('project_policy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.PricePolicy', verbose_name='价格策略')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.Userinfo', verbose_name='用户')),
            ],
        ),
    ]