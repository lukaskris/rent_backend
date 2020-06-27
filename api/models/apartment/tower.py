from django.db import models

from api.models.apartment.apartment import Apartment


class Tower(models.Model):
    name = models.CharField(max_length=200, default='')
    apartment = models.ForeignKey(Apartment, on_delete=models.PROTECT)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']