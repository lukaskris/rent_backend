from django.db import models


class Apartment(models.Model):
    name = models.TextField(default="")
    location = models.TextField()
