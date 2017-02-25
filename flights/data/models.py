from django.db import models


class Enroute(models.Model):
    ident = models.CharField(max_length=255, blank=True)               # "NAX1318"
    aircrafttype = models.CharField(max_length=255, blank=True)        # "B738"
    actualdeparturetime = models.IntegerField(default=0, null=True)    # 0
    estimatedarrivaltime = models.IntegerField(default=0, null=True)   # 1486930380
    filed_departuretime = models.IntegerField(default=0, null=True)    # 1486923000
    origin = models.CharField(max_length=255, blank=True)              # "ENBR"
    destination = models.CharField(max_length=255, blank=True)         # "EGKK"
    originName = models.CharField(max_length=255, blank=True)          # "Bergen, Flesland"
    originCity = models.CharField(max_length=255, blank=True)          # "Bergen, Hordaland"
    destinationName = models.CharField(max_length=255, blank=True)     # "London Gatwick"
    destinationCity = models.CharField(max_length=255, blank=True)     # "London, England"
