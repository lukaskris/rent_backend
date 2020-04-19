# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import uuid
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from django.utils.timezone import now
import os


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


class Apartment(models.Model):
    name = models.TextField(default="")
    location = models.TextField()

# Type Penjualan
class TypeSelling(models.Model): # 1 sewa harian, 2 sewa mingguan ..., 5 jual
    name = models.TextField()

# Status orderç
# 1. Need Payment
# 2. Payment Success
# 3. Payment Fail
# 4.
class OrderStatus(models.Model):
    name = models.TextField()

# Products model
class Product(models.Model):
    product_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, default="")
    description = models.TextField(default="")
    status = models.BooleanField(default=True) # 0 1 active or not
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)

class Room(Product):
    room_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bedroom_total = models.IntegerField(default=1)
    guest_maximum = models.IntegerField(default=1)
    bathroom_total = models.IntegerField(default=1)
    sqm_room = models.IntegerField(default=24)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    apartment = models.ForeignKey(Apartment, on_delete=models.DO_NOTHING, null=True)
    contact_person_name = models.CharField(max_length=200, default="")
    contact_person_phone = models.CharField(max_length=200, default="")

class Feature(Product): #laundry cuci ac dll
    feature_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

# ads bundle
class AdsBundle(Product):
    ads_bundle_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_click = models.IntegerField()


# Product detail model
class RoomDetail(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room_detail', blank=True, null=True)
    type_selling = models.ForeignKey(TypeSelling, on_delete=models.DO_NOTHING)
    price = models.DecimalField(max_digits=12, decimal_places=2)

class RoomFeature(models.Model):
    feature = models.ForeignKey(Feature, on_delete=models.DO_NOTHING)
    room_detail = models.ForeignKey(RoomDetail, on_delete=models.DO_NOTHING)
    price = models.DecimalField(max_digits=10, decimal_places=2)


from uuid import uuid4
from django.utils.deconstruct import deconstructible

@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(self.path, filename)

path_and_rename_products = PathAndRename("images/products/")
path_and_rename_banner = PathAndRename("images/banners/")

# Images models
class RoomImages(models.Model):
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='room_images', blank=True, null=True)
    image = models.FileField(upload_to=path_and_rename_products, verbose_name='Room')

class Banner(models.Model):
    url = models.TextField()
    image = models.FileField(upload_to=path_and_rename_banner, verbose_name='Banner')
    active_at = models.DateTimeField(auto_now_add=False)
    expired_at = models.DateTimeField(auto_now_add=False)

# Ads model
class RoomAd(models.Model):
    room = models.ForeignKey(Room, on_delete=models.PROTECT)
    click = models.IntegerField(default=0) #10x click
    expired_date = models.DateTimeField()
    start_date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

# ads order
class AdsOrder(models.Model):
    class Meta:
        unique_together = [['id', 'midtrans_id']]
    bundle = models.ForeignKey(AdsBundle, on_delete=models.PROTECT)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    midtrans_id = models.TextField(default="")
    expired_date = models.DateTimeField(default=None)
    payment_date = models.DateTimeField(default=None)
    order_status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT, default=None)

# Payments header
class OrderHeader(models.Model):
    class Meta:
        unique_together = [['id', 'midtrans_id', 'invoice_ref_number']]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    midtrans_id = models.TextField(default="")
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    type_selling = models.ForeignKey(TypeSelling, on_delete=models.DO_NOTHING, default=None, blank=None, null=True)
    invoice_ref_number = models.TextField()
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    order_date = models.DateTimeField(auto_now_add=True)
    expired_date = models.DateTimeField()
    payment_date = models.DateTimeField()
    order_status = models.ForeignKey(OrderStatus, on_delete=models.DO_NOTHING)
    payment_type = models.TextField(null=True)
    payment_number = models.TextField(null=True)
    check_in_time = models.DateTimeField()
    check_out_time = models.DateTimeField()

# Payments detail
class OrderDetail(models.Model):
    order_header = models.ForeignKey(OrderHeader, on_delete=models.PROTECT)
    feature = models.ForeignKey(Feature, on_delete=models.DO_NOTHING)
    price = models.DecimalField(max_digits=10, decimal_places=2) #price

class Notification(models.Model):
    notification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    message = models.TextField(default="")
    order_header = models.ForeignKey(OrderHeader, on_delete=models.DO_NOTHING, default=None, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


def __str__(self):
    return '%s %s' % (self.name, self.body)
