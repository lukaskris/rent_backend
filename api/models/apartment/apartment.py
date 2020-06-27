from django.db import models

from api.models.location.location import Location


class Apartment(models.Model):
    name = models.TextField(default="")
    location = models.ForeignKey(Location, blank=True, null=True, on_delete=models.DO_NOTHING)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
