# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

# Users model
class User(models.Model):
    id = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    name = models.TextField()
    image_url = models.CharField(max_length=200)
    token = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

# Products model
class Product(models.Model):
    id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)

# Ads model
class Ad(models.Model):
    id = models.CharField(max_length=200)
    product_id = models.CharField(max_length=200)
    expired_date = models.DateTimeField()
    start_date = models.DateTimeField()
    active = models.BooleanField()

# Payments header
class Payment(models.Model):
    id = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

# Payments detail
class PaymentDetail(models.Model):
    id = models.CharField()
    payment_id = models.CharField()
    product_id = models.CharField()
    length = models.CharField()


def __str__(self):
    return '%s %s' % (self.name, self.body)
