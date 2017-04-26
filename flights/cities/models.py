from django.db import models


# Create your models here.
class City(models.Model):
    city = models.fields.CharField(max_length=255)
    iata = models.fields.CharField(max_length=255, unique=True)
    created = models.fields.DateTimeField(auto_now_add=True)
    modified = models.fields.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'cities'
