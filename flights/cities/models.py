from django.db import models


# Create your models here.
class City(models.Model):
    city = models.fields.CharField(max_length=255, unique=True)
    iata = models.fields.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'cities'
