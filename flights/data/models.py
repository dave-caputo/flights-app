from django.db import models


class Enroute(models.Model):
    ident = models.CharField(max_length=255, default='')            # "NAX1318"
    aircrafttype = models.CharField(max_length=255, default='')     # "B738"
    actualdeparturetime = models.IntegerField(default=0)            # 0
    estimatedarrivaltime = models.IntegerField(default=0)           # 1486930380
    filed_departuretime = models.IntegerField(default=0)            # 1486923000
    origin = models.CharField(max_length=255, default='')           # "ENBR"
    destination = models.CharField(max_length=255, default='')      # "EGKK"
    originName = models.CharField(max_length=255, default='')       # "Bergen, Flesland"
    originCity = models.CharField(max_length=255, default='')       # "Bergen, Hordaland"
    destinationName = models.CharField(max_length=255, default='')  # "London Gatwick"
    destinationCity = models.CharField(max_length=255, default='')  # "London, England"
