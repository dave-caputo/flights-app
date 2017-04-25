# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-04-25 19:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cities', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='city',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]