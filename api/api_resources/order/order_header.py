import datetime
import decimal
import json
import logging
from datetime import timedelta, datetime
from decimal import Decimal

import requests
from django.conf import settings
from django.conf.urls import url
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.utils import timezone
from tastypie import fields
from tastypie.constants import ALL
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS

# models
from api.api_resources.aparment.apartment_resource import ApartmentResource
from api.api_resources.aparment.tower_resource import TowerResource
from api.api_resources.order.order_status_resource import OrderStatusResource
from api.api_resources.order.type_selling import TypeSellingResource
from api.api_resources.product.product_resource import ProductResource
from api.api_resources.user_resource import UserResource
from api.models.apartment.apartment import Apartment
from api.models.apartment.tower import Tower
from api.models.benefit.commission_percentage import CommissionPercentage
from api.models.order.order_header import OrderHeader
from api.models.room.feature import Feature
from api.models.room.room import Room
from api.models.user.user import User
from api.util.utils import render_to_pdf

logger = logging.getLogger('api.order_header')


class OrderHeaderResource(ModelResource):
    type_selling = fields.ToOneField(TypeSellingResource, attribute='type_selling', full=True, null=True)
    tower = fields.ToOneField(TowerResource, attribute='tower', full=True, null=True)
    apartment = fields.ToOneField(ApartmentResource, attribute='apartment', full=True, null=True)
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
            'order_date': ALL,
            'order_status': ALL_WITH_RELATIONS,
            'apartment': ALL_WITH_RELATIONS
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
            # report admin
            url(r"^(?P<resource_name>%s)/report_monthly/"
                r"" %
                resource_name,
                self.wrap_view('admin_report_monthly'), name="api_admin_report_view"),
            # report marketing
            url(r"^(?P<resource_name>%s)/report_monthly_marketing/"
                r"" %
                resource_name,
                self.wrap_view('admin_report_monthly_marketing'), name="api_admin_report_marketing_view"),
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
            datetime_test = timezone.now().today()
            order_header_today = self.nonechecker(OrderHeader.objects.filter(
                type_selling__isnull=False,
                order_status_id=2,
                active=True,
                order_date__day=datetime_test.day
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
                customField = data['custom_field1']
                customFieldJson = json.loads(customField)
                checkIn = customFieldJson['check_in']
                checkOut = customFieldJson['check_out']
                type_selling_id = customFieldJson['type_selling_id']
                user_id = data['custom_field2']
                type_product = customFieldJson['type_product']
                items = data['item_details']

                if type_product == "product":
                    order_header = OrderHeader.objects.create(
                        midtrans_id=data["transaction_details"]["order_id"],
                        product_id=items[0]['id'],
                        type_selling_id=type_selling_id,
                        grand_total=data['transaction_details']['gross_amount'],
                        user_id=user_id,
                        payment_date=timezone.now(),
                        order_status_id=1,
                        apartment=None,
                        tower=None,
                        description="",
                        phone="",
                        expired_date=timezone.now() + timedelta(days=1),
                        check_in_time=datetime.strptime(checkIn, DATETIME_FORMAT),
                        check_out_time=datetime.strptime(checkOut, DATETIME_FORMAT)
                    )
                elif type_product == "ads":
                    order_header = OrderHeader.objects.create(
                        midtrans_id=data["transaction_details"]["order_id"],
                        product_id=data['item_details'][0]['id'],
                        type_selling_id=None,
                        grand_total=data['transaction_details']['gross_amount'],
                        user_id=user_id,
                        payment_date=timezone.now(),
                        order_status_id=1,
                        apartment=None,
                        tower=None,
                        description="",
                        phone="",
                        expired_date=timezone.now() + timedelta(days=1),
                        check_in_time=timezone.now(),
                        check_out_time=timezone.now()
                    )
                else:
                    customField3 = json.loads(data['custom_field3'])
                    tower_id = customField3['tower_id']
                    apartment_id = customField3['apartment_id']
                    phone = customField3['phone']
                    description = customField3['description']

                    tower = Tower.objects.get(pk=tower_id)
                    apartment = Apartment.objects.get(pk=apartment_id)
                    feature = Feature.objects.get(pk=data['item_details'][0]['id'])

                    order_header = OrderHeader.objects.create(
                        midtrans_id=data["transaction_details"]["order_id"],
                        product_id=feature.product_id,
                        type_selling_id=None,
                        grand_total=data['transaction_details']['gross_amount'],
                        user_id=user_id,
                        payment_date=timezone.now(),
                        order_status_id=1,
                        apartment=apartment,
                        tower=tower,
                        description=description,
                        phone=phone,
                        expired_date=timezone.now() + timedelta(days=1),
                        check_in_time=datetime.strptime(checkIn, DATETIME_FORMAT),
                        check_out_time=datetime.strptime(checkIn, DATETIME_FORMAT)
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


        except Exception as e:
            print("Exception: {}".format(e))
            return JsonResponse({
                'error': {
                    "message": str(e)
                }
            }, content_type='application/json', status=500)

    def admin_report_monthly(self, request, **kwargs):
        percentage = CommissionPercentage.objects.first().percentage
        datetime_test = timezone.now().today()
        order_header_month = decimal.Decimal(0)
        details = []

        orders_data = OrderHeader.objects.filter(
            type_selling__isnull=False,
            order_status_id=2,
            active=True,
            order_date__month=datetime_test.month
        )

        for data in orders_data:
            detail_product = Room.objects.get(pk=data.product.product_id)
            income = data.grand_total * ((10 - percentage) / 100)
            owner_commission = data.grand_total - income
            order_header_month += decimal.Decimal(data.grand_total)
            different_date = data.check_out_time - data.check_in_time
            month = different_date.days // 30
            year = different_date.days // 365
            days = different_date.days % 30

            if month == 0:
                duration = "%d hari" % (days)
            elif 0 < month < 12:
                if days > 0:
                    duration = "%d bulan %d hari" % (month, days)
                else:
                    duration = "%d bulan" % (month)
            else:
                duration = "%d tahun" % (year)

            details.append(
                {
                    'name': detail_product.name,
                    "apartment": detail_product.apartment.name,
                    "tower": detail_product.tower.name,
                    "description": detail_product.description,
                    "duration": duration,
                    'invoice': data.invoice,
                    "checkin": data.check_in_time.strftime("%d/%M%Y"),
                    "checkout": data.check_out_time.strftime("%d/%M%Y"),
                    "marketing_name": detail_product.contact_person_name,
                    "marketing_phone": detail_product.contact_person_phone,
                    'owner_commission': 'IDR {:20,.0f}'.format(owner_commission),
                    'office_commission': 'IDR {:20,.0f}'.format(income),

                }
            )

        details.append(
            {
                "invoice": "SE/029101",
                'name': "Ruangan ABC",
                "apartment": "Apartement A",
                "tower": "Tower B",
                "description": "Unit 1401",
                "duration": "1 bulan",
                "checkin": "10/04/2020",
                "checkout": "09/05/2020",
                "marketing_name": "Budi",
                "marketing_phone": "08918181811",
                'owner_commission': "IDR 4.300.000.000",
                'office_commission': "IDR 172.000.000",

            }
        )

        admin_balance_month = order_header_month * ((10 - percentage) / 100)
        total_rent = order_header_month - admin_balance_month

        context = {
            "month": datetime_test.strftime('%B'),
            "total_income": 'IDR {:20,.0f}'.format(admin_balance_month),
            "total_rent": 'IDR {:20,.0f}'.format(total_rent),
            "date": datetime_test.strftime("%d %B %Y"),
            "details": details
        }
        pdf = render_to_pdf('report.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Report_%s.pdf" % int(datetime_test.timestamp())
            content = "inline; filename='%s'" % (filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")


    def admin_report_monthly_marketing(self, request, **kwargs):
        user_id = request.GET.get('user_id', 0)
        user = User.objects.get(pk=user_id)
        percentage = CommissionPercentage.objects.first().percentage
        datetime_test = timezone.now().today()
        order_header_month = decimal.Decimal(0)
        details = []

        orders_data = OrderHeader.objects.filter(
            type_selling__isnull=False,
            order_status_id=2,
            active=True,
            order_date__month=datetime_test.month
        )

        for data in orders_data:
            detail_product = Room.objects.get(pk=data.product.product_id)
            income = data.grand_total * ((10 - percentage) / 100)
            owner_commission = data.grand_total - income
            order_header_month += decimal.Decimal(data.grand_total)
            different_date = data.check_out_time - data.check_in_time
            month = different_date.days // 30
            year = different_date.days // 365
            days = different_date.days % 30

            if month == 0:
                duration = "%d hari" % (days)
            elif 0 < month < 12:
                if days > 0:
                    duration = "%d bulan %d hari" % (month, days)
                else:
                    duration = "%d bulan" % (month)
            else:
                duration = "%d tahun" % (year)

            details.append(
                {
                    'name': detail_product.name,
                    "apartment": detail_product.apartment.name,
                    "tower": detail_product.tower.name,
                    "description": detail_product.description,
                    "duration": duration,
                    'invoice': data.invoice,
                    "checkin": data.check_in_time.strftime("%d/%M%Y"),
                    "checkout": data.check_out_time.strftime("%d/%M%Y"),
                    "marketing_name": detail_product.contact_person_name,
                    "marketing_phone": detail_product.contact_person_phone,
                    'owner_commission': 'IDR {:20,.0f}'.format(owner_commission),
                    'commission': 'IDR {:20,.0f}'.format(income),

                }
            )

        details.append(
            {
                "invoice": "SE/029101",
                'name': "Ruangan ABC",
                "apartment": "Apartement A",
                "tower": "Tower B",
                "description": "Unit 1401",
                "duration": "1 bulan",
                "checkin": "10/04/2020",
                "checkout": "09/05/2020",
                "marketing_name": "Budi",
                "marketing_phone": "08918181811",
                'owner_commission': "IDR 4.300.000",
                'commission': "IDR 258.000",

            }
        )
        marketing_balance_month = order_header_month * (percentage / 100)
        total_rent = order_header_month - marketing_balance_month

        context = {
            "name": user.name,
            "phone": user.phone_number,
            "month": datetime_test.strftime('%B'),
            "total_income": 'IDR {:20,.0f}'.format(marketing_balance_month),
            "total_rent": 'IDR {:20,.0f}'.format(total_rent),
            "date": datetime_test.strftime("%d %B %Y"),
            "details": details
        }
        pdf = render_to_pdf('report_marketing.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Report_%s.pdf" % int(datetime_test.timestamp())
            content = "inline; filename='%s'" % (filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")