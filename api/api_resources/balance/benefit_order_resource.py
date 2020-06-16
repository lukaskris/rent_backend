from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.resources import ModelResource

from api.api_resources.order.order_header import OrderHeaderResource
from api.models.benefit.benefit_order import BenefitOrder


class BenefitOrderResource(ModelResource):
    order = fields.ToOneField(OrderHeaderResource, attribute="order", full=True, null=True)

    class Meta:
        queryset = BenefitOrder.objects.all()
        resource_name = 'benefit_order'
        filtering = {
            'user': ALL_WITH_RELATIONS
        }
        authorization = Authorization()
