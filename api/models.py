# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import uuid
from django.utils.translation import ugettext_lazy as _

class UserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        user=self._create_user(email, password, True, True, **extra_fields)
        return user

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=254, unique=True)
    name = models.CharField(max_length=254, null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    image_url = models.FileField(blank=False, null=False, upload_to='images/employees/', default='')

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __unicode__(self):
        return self.username

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def get_absolute_url(self):
        return "/users/%i/" % (self.pk)

# Status orderç
# 1. Need Payment
# 2. Payment Success
# 3. Payment Fail
# 4.
class OrderStatus(models.Model):
    name = models.TextField()

# Products model
class Products(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    description = models.TextField(default="")
    status = models.BooleanField() # 0 1 active or not
    contact_person_name = models.CharField(max_length=200)
    contact_person_phone = models.CharField(max_length=200)

# Images models
class ProductImages(models.Model):
    product = models.ForeignKey(Products, on_delete=models.PROTECT, related_name='product')
    image = models.FileField(upload_to='images/products/', verbose_name='Products')

class Features(models.Model): #laundry cuci ac dll
    name = models.TextField()
    status = models.BooleanField() # 0 1 active or not
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

# Type Penjualan
class TypeSelling(models.Model): # 1 sewa harian, 2 sewa mingguan ..., 5 jual
    name = models.TextField()

# Ads model
class Ads(models.Model):
    product = models.ForeignKey(Products, on_delete=models.PROTECT)
    click = models.IntegerField() #10x click
    expired_date = models.DateTimeField()
    start_date = models.DateTimeField()
    active = models.BooleanField()

# ads bundle
class AdsBundle(models.Model):
    name = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

# ads order
class AdsOrder(models.Model):
    bundle = models.ForeignKey(AdsBundle, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)

# Product detail model
class ProductsDetail(models.Model):
    product = models.ForeignKey(Products, on_delete=models.PROTECT, default=None, related_name='product_detail')
    type_selling = models.ForeignKey(Features, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=12, decimal_places=2)

class ProductsDetailFeatures(models.Model):
    features = models.ForeignKey(Features, on_delete=models.PROTECT)
    product_detail = models.ForeignKey(ProductsDetail, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)

# Payments header
class OrderHeader(models.Model):
    class Meta:
        unique_together = [['id', 'midtrans_id', 'invoice_ref_number']]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    midtrans_id = models.TextField(default="")
    product = models.ForeignKey(Products, on_delete=models.PROTECT)
    type_selling = models.ForeignKey(TypeSelling, on_delete=models.PROTECT)
    invoice_ref_number = models.TextField()
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    order_date = models.DateTimeField(auto_now_add=True)
    expired_date = models.DateTimeField()
    payment_date = models.DateTimeField()
    order_status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT)
    check_in_time = models.DateTimeField()
    check_out_time = models.DateTimeField()

# Payments detail
class OrderDetail(models.Model):
    order_header = models.ForeignKey(OrderHeader, on_delete=models.PROTECT)
    feature = models.ForeignKey(Features, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2) #price


def __str__(self):
    return '%s %s' % (self.name, self.body)
