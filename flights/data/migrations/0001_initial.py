# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-25 12:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Enroute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ident', models.CharField(default='', max_length=255)),
                ('aircrafttype', models.CharField(default='', max_length=255)),
                ('actualdeparturetime', models.IntegerField(default=0)),
                ('estimatedarrivaltime', models.IntegerField(default=0)),
                ('filed_departuretime', models.IntegerField(default=0)),
                ('origin', models.CharField(default='', max_length=255)),
                ('destination', models.CharField(default='', max_length=255)),
                ('originName', models.CharField(default='', max_length=255)),
                ('originCity', models.CharField(default='', max_length=255)),
                ('destinationName', models.CharField(default='', max_length=255)),
                ('destinationCity', models.CharField(default='', max_length=255)),
            ],
        ),
    ]
