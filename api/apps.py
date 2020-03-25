# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.db.models import signals

# class ApiConfig(AppConfig):
#     name = 'api'
#     def ready(self):
#         from api.models import User
#         from tastypie.models import create_api_key
#         print("Create API Key for User")
#         print(User)
#         signals.post_save.connect(create_api_key, sender=User)
