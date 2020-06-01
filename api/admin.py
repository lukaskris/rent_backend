# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
from api.models.ads.ad_bundle import AdsBundle
from api.models.apartment.apartment import Apartment
from api.models.banner.banner import Banner
from api.models.order.order_header import OrderHeader
from api.models.room.room import Room
from api.models.user.user import User


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password', 'name', 'last_login', 'image_url')}),
        ('Permissions', {'fields': (
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions',
        )}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2')
            }
        ),
    )

    list_display = ('email', 'name', 'is_staff', 'last_login')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

    def has_delete_permission(self, request, obj=None):
        return False



class AdsBundleAdmin(admin.ModelAdmin):
    list_display = ('ads_bundle_id', 'name', 'total_click', 'price',)

    def has_delete_permission(self, request, obj=None):
        return False


class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_id', 'name', 'description', 'contact_person_name', 'contact_person_phone', 'created_by')

    def has_delete_permission(self, request, obj=None):
        return False


class OrderHeaderAdmin(admin.ModelAdmin):
    list_display = (
        'midtrans_id', 'invoice_ref_number', 'grand_total', 'order_date', 'expired_date', 'payment_date',
        'payment_type',
        'payment_number', 'type_selling')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ApartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')

    def has_delete_permission(self, request, obj=None):
        return False


class BannerAdmin(admin.ModelAdmin):
    list_display = ('active_at', 'expired_at', 'image')

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(User, UserAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(AdsBundle, AdsBundleAdmin)
admin.site.register(OrderHeader, OrderHeaderAdmin)
admin.site.register(Apartment, ApartmentAdmin)
admin.site.register(Banner, BannerAdmin)
