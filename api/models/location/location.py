from django.db import models


# ac cleaning dan room cleaning
class Location(models.Model):
    name = models.CharField(max_length=200, default="")
    active = models.BooleanField(default=True)
