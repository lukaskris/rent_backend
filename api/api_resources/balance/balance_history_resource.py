import decimal

from django.conf.urls import url
from django.db import transaction
from django.http import JsonResponse
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.resources import ModelResource

from api.api_resources.balance.benefit_order_resource import BenefitOrderResource
from api.api_resources.user_resource import UserResource
from api.models.benefit.benefit_staff import BalanceHistory, BalanceStaff


class BalanceHistoryResource(ModelResource):
    benefit_order = fields.ToOneField(BenefitOrderResource, attribute='benefit_order', full=True, null=True)
    user = fields.ToOneField(UserResource, attribute="user", full=True, null=False)

    class Meta:
        queryset = BalanceHistory.objects.all().order_by("-created_at")
        resource_name = 'balance_history'
        filtering = {
            'user': ALL_WITH_RELATIONS
        }
        authorization = Authorization()

    def prepend_urls(self):
        """ Add the following array of urls to the UserResource base urls """
        resource_name = self._meta.resource_name
        return [
            # charge
            url(r"^(?P<resource_name>%s)/pay_staff" %
                resource_name,
                self.wrap_view('pay_staff'), name="api_pay_staff")
        ]

    def pay_staff(self, request, **kwargs):
        try:
            data = self.deserialize(
                request, request.body,
                format=request.content_type
            )
            user_id = data.get('user_id', "")
            nominal = data.get("nominal", 0)

            if not user_id:
                # empty user_id
                return JsonResponse({
                    'error': {
                        "message": "Invalid user id"
                    }
                }, content_type='application/json', status=500)

            with transaction.atomic():
                try:
                    balance_staff = BalanceStaff.objects.get(user_id=user_id)
                    balance_staff.balance = balance_staff.balance + decimal.Decimal(nominal)
                    balance_staff.save()
                    # save to history
                    balance_history = BalanceHistory.objects.create(
                        user_id=user_id,
                        nominal=nominal
                    )
                    return JsonResponse({
                        "id": balance_history.id,
                        "user": {
                            "id": balance_history.user_id
                        },
                        "nominal": balance_history.nominal
                    }, content_type='application/json', status=200)
                except BalanceStaff.DoesNotExist:
                    balance_staff = BalanceStaff.objects.create(
                        user_id=user_id,
                        balance=0
                    )
                    balance_staff.balance = balance_staff.balance + decimal.Decimal(nominal)
                    balance_staff.save()
                    # save to history
                    balance_history = BalanceHistory.objects.create(
                        user_id=user_id,
                        nominal=nominal
                    )
                    return JsonResponse({
                        "id": balance_history["id"],
                        "user": {
                            "id": balance_history["user_id"]
                        },
                        "nominal": balance_history["nominal"]
                    }, content_type='application/json', status=200)
        except Exception as e:
            return JsonResponse({
                'error': {
                    "message": str(e)
                }
            }, content_type='application/json', status=500)
