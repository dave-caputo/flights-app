from django.db import models


class Enroute(models.Model):
    ident = models.CharField(max_length=255)            # "NAX1318"
    aircrafttype = models.CharField(max_length=255)     # "B738"
    actualdeparturetime = models.IntegerField()         # 0
    estimatedarrivaltime = models.IntegerField()        # 1486930380
    filed_departuretime = models.IntegerField()         # 1486923000
    origin = models.CharField(max_length=255)           # "ENBR"
    destination = models.CharField(max_length=255)      # "EGKK"
    originName = models.CharField(max_length=255)       # "Bergen, Flesland"
    originCity = models.CharField(max_length=255)       # "Bergen, Hordaland"
    destinationName = models.CharField(max_length=255)  # "London Gatwick"
    destinationCity = models.CharField(max_length=255)  # "London, England"
