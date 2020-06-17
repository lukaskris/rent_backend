import datetime
import json
import logging
from datetime import timedelta, datetime
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

import requests
from django.conf import settings
from django.conf.urls import url
from django.db.models import Q, Sum
from django.http import HttpResponse, JsonResponse
from tastypie import fields
from tastypie.constants import ALL
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS

# models
from api.api_resources.order.order_status_resource import OrderStatusResource
from api.api_resources.order.type_selling import TypeSellingResource
from api.api_resources.product.product_resource import ProductResource
from api.api_resources.user_resource import UserResource
from api.models.benefit.commission_percentage import CommissionPercentage
from api.models.order.order_header import OrderHeader

logger = logging.getLogger('api.order_header')


class OrderHeaderResource(ModelResource):
    type_selling = fields.ToOneField(TypeSellingResource, attribute='type_selling', full=True, null=True)
    order_status = fields.ToOneField(OrderStatusResource, attribute='order_status', full=True, null=True)
    product = fields.ToOneField(ProductResource, attribute='product', full=True, null=True)
    user = fields.ToOneField(UserResource, attribute='user', full=True, null=True)

    class Meta:
        queryset = OrderHeader.objects.all()
        resource_name = 'order'
        ordering = ['order_date', 'order_status']
        filtering = {
            'user': ALL_WITH_RELATIONS,
            'id': ['exact'],
            'product': ALL_WITH_RELATIONS,
            'check_in_time': ALL,
            'check_out_time': ALL,
            'type_selling': ALL_WITH_RELATIONS,
            'active': ALL,
            'order_date': ALL
        }

    def prepend_urls(self):
        """ Add the following array of urls to the UserResource base urls """
        resource_name = self._meta.resource_name
        return [
            # charge
            url(r"^(?P<resource_name>%s)/charge$" %
                resource_name,
                self.wrap_view('charge'), name="api_charge"),
            # report
            url(r"^(?P<resource_name>%s)/admin_report"
                r"" %
                resource_name,
                self.wrap_view('admin_report'), name="api_admin_report"),
        ]

    def nonechecker(self, value):
        if value is None:
            return Decimal(0.0)
        else:
            return value

    def admin_report(self, request, **kwargs):
        try:
            percentage = CommissionPercentage.objects.first().percentage
            # datetime_test = datetime.strptime('May 23 2020', '%b %d %Y')
            datetime_test = timezone.now()
            order_header_today = self.nonechecker(OrderHeader.objects.filter(
                type_selling__isnull=False,
                order_status_id=2,
                active=True,
                order_date=datetime_test
            ).aggregate(Sum('grand_total'))["grand_total__sum"])
            commission_today = order_header_today * (percentage / 100)
            admin_balance_today = order_header_today * ((10 - percentage) / 100)

            order_header_week = self.nonechecker(OrderHeader.objects.filter(
                type_selling__isnull=False,
                order_status_id=2,
                active=True,
                order_date__week=int(datetime_test.strftime("%V"))
            ).aggregate(Sum('grand_total'))["grand_total__sum"])
            commission_week = order_header_week * (percentage / 100)
            admin_balance_week = order_header_week * ((10 - percentage) / 100)

            order_header_month = self.nonechecker(OrderHeader.objects.filter(
                type_selling__isnull=False,
                order_status_id=2,
                active=True,
                order_date__month=datetime_test.month
            ).aggregate(Sum('grand_total'))["grand_total__sum"])
            commission_month = order_header_month * (percentage / 100)
            admin_balance_month = order_header_month * ((10 - percentage) / 100)

            return JsonResponse({
                'objects': [
                    {
                        "date_type": "hari",
                        "total_selling": order_header_today,
                        "commission": commission_today,
                        "company": admin_balance_today
                    },
                    {
                        "date_type": "minggu",
                        "total_selling": order_header_week,
                        "commission": commission_week,
                        "company": admin_balance_week
                    },
                    {
                        "date_type": "bulan",
                        "total_selling": order_header_month,
                        "commission": commission_month,
                        "company": admin_balance_month
                    }
                ]
            }, content_type='application/json', status=200)
        except Exception as e:
            print("Exception: {}".format(e))
            return JsonResponse({
                'error': {
                    "message": str(e)
                }
            }, content_type='application/json', status=500)

    def charge(self, request, **kwargs):
        try:
            with transaction.atomic():
                logger.info('OrderHeaderResource.payment')
                data = self.deserialize(
                    request, request.body,
                    format=request.content_type
                )

                print('OrderHeaderResource.payment: {}'.format(json.dumps(data)))

                import base64

                auth = settings.MIDTRANS_SERVER_KEY_SANDBOX
                base64_bytes = base64.b64encode(auth.encode('ascii'))
                base64_auth = base64_bytes.decode('ascii')

                headers = {
                    'Authorization': 'Basic ' + base64_auth,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }

                DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
                customField2 = data['custom_field2'].split('|')
                checkIn = customField2[0]
                checkOut = customField2[1]

                if "custom_field1" in data:
                    order_header = OrderHeader.objects.create(
                        midtrans_id=data["transaction_details"]["order_id"],
                        product_id=data['item_details'][0]['id'],
                        type_selling_id=data['custom_field1'],
                        grand_total=data['transaction_details']['gross_amount'],
                        user_id=data['custom_field3'],
                        payment_date=timezone.now(),
                        order_status_id=1,
                        expired_date=timezone.now() + timedelta(days=1),
                        check_in_time=datetime.strptime(checkIn, DATETIME_FORMAT),
                        check_out_time=datetime.strptime(checkOut, DATETIME_FORMAT)
                    )

                    response = requests.request("POST", settings.MIDTRANS_SANDBOX, headers=headers,
                                                data=json.dumps(data))
                    print(response.json())
                    if response.status_code == 201:
                        order_header.save()
                    else:
                        order_header.delete()
                    return HttpResponse(
                        content=response.content,
                        status=response.status_code,
                        content_type=response.headers['Content-Type']
                    )
                else:
                    order_header = OrderHeader.objects.create(
                        midtrans_id=data["transaction_details"]["order_id"],
                        product_id=data['item_details'][0]['id'],
                        type_selling_id=None,
                        grand_total=data['transaction_details']['gross_amount'],
                        user_id=data['custom_field3'],
                        payment_date=timezone.now(),
                        order_status_id=1,
                        expired_date=timezone.now() + timedelta(days=1),
                        check_in_time=timezone.now(),
                        check_out_time=timezone.now()
                    )

                    response = requests.request("POST", settings.MIDTRANS_SANDBOX, headers=headers,
                                                data=json.dumps(data))
                    print(response.json())
                    if response.status_code == 201:
                        order_header.save()
                    return HttpResponse(
                        content=response.content,
                        status=response.status_code,
                        content_type=response.headers['Content-Type']
                    )


        except Exception as e:
            print("Exception: {}".format(e))
            return JsonResponse({
                'error': {
                    "message": str(e)
                }
            }, content_type='application/json', status=500)
