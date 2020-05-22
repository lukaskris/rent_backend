import datetime
import json
import logging
from datetime import datetime as dtime, timedelta
from operator import itemgetter

import requests
from django.conf import settings
from django.conf.urls import url
from django.contrib.auth import authenticate, login, logout
from django.core.serializers.json import DjangoJSONEncoder
from django.db import connection
from django.db.models import Q
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.http import JsonResponse
from fcm_django.models import FCMDevice
from tastypie import fields
from tastypie import http
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization
from tastypie.constants import ALL
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS
from tastypie.utils import trailing_slash

from api.models import Apartment, OrderStatus, Room, Banner, Product, Feature, Notification, RoomAd, AdsBundle, \
    AdsOrder, OrderHeader, TypeSelling, OrderDetail, RoomImages, RoomDetail
# models
from api.models import User