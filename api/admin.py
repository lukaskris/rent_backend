# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
from api.models import User, Room, AdsBundle, Feature, TypeSelling, AdsOrder, OrderHeader

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


class TypeSellingAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

admin.site.register(User, UserAdmin)
admin.site.register(Room, admin.ModelAdmin)
admin.site.register(Feature, admin.ModelAdmin)
admin.site.register(TypeSelling, TypeSellingAdmin)
admin.site.register(AdsOrder)
admin.site.register(AdsBundle)
admin.site.register(OrderHeader)
