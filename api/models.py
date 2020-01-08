# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Employees(models.Model):
    name = models.CharField(max_length=200)
    phone = models.TextField()
    email = models.TextField()
    image_url = models.FileField(blank=False, null=False, upload_to='images/employees/', default='')

# Users model
class Users(models.Model):
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    name = models.TextField()
    phone = models.TextField()
    image_url = models.FileField(blank=False, null=False, upload_to='images/users/', default='')
    token = models.CharField(max_length=200)
    status = models.BooleanField() # active or not
    created_at = models.DateTimeField(auto_now_add=True)

# Products model
class Products(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'Employees',
        on_delete=models.CASCADE,
    ) # reference to employees
    status = models.BooleanField() # 0 1 active or not
    attachments = models.FileField(blank=False, null=False, upload_to='images/products/') # ex: /images/file_1.jpg,/images/file_1.mp4
    contact_person_name = models.CharField(max_length=200)
    contact_person_phone = models.CharField(max_length=200)

# Product detail model
class ProductsDetail(models.Model):
    parent_id = models.CharField(max_length=200)
    type_selling = models.ForeignKey(
        'Features',
        on_delete=models.CASCADE,
    )
    price = models.DecimalField(max_digits=12, decimal_places=2)

class ProductsDetailFeatures(models.Model):
    features = models.ForeignKey(
        'Features',
        on_delete=models.CASCADE,
    )
    product_detail = models.ForeignKey(
        'ProductsDetail'
    ) #ke products detail
    price = models.DecimalField(max_digits=10, decimal_places=2)

class Features(models.Model): #laundry cuci ac dll
    name = models.TextField()
    status = models.BooleanField() # 0 1 active or not
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'Employees'
    ) # reference to employees

# Type Penjualan
class TypeSelling(models.Model): # 1 sewa harian, 2 sewa mingguan ..., 5 jual
    name = models.TextField()

# Ads model
class Ad(models.Model):
    product = models.ForeignKey(
        'Products',
    )
    click = models.IntegerField() #10x click
    expired_date = models.DateTimeField()
    start_date = models.DateTimeField()
    active = models.BooleanField()

# ads order
class AdsOrder(models.Model):
    bundle = models.ForeignKey(
        'AdsBundle'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)

# ads bundle
class AdsBundle(models.Model):
    name = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

# Payments header
class OrderHeader(models.Model):
    product = models.ForeignKey(
        'Products',
    )
    type_selling = models.ForeignKey(
        'TypeSelling'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    invoice_ref_number = models.TextField()
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(
        'Users',
    )
    order_date = models.DateTimeField(auto_now_add=True)
    expired_date = models.DateTimeField()
    payment_date = models.DateTimeField()
    order_status = models.ForeignKey(
        'OrderStatus'
    )
    check_in_time = models.DateTimeField()
    check_out_time = models.DateTimeField()

# Payments detail
class OrderDetail(models.Model):
    order_header = models.ForeignKey(
        'OrderHeader'
    )
    feature = models.ForeignKey(
        'Features'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2) #price

# Status order
class OrderStatus(models.Model):
    name = models.TextField()

def __str__(self):
    return '%s %s' % (self.name, self.body)
