from django.db import models


class Apartment(models.Model):
    name = models.TextField(default="")
    location = models.TextField()
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name
