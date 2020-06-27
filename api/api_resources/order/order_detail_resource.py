from django_filters import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.resources import ModelResource

from api.api_resources.order.order_header import OrderHeaderResource
from api.models.order.order_detail import OrderDetail


class OrderDetailResource(ModelResource):
    order_header = fields.ToOneField(OrderHeaderResource, attribute='order_header', full=True, null=True)

    class Meta:
        queryset = OrderDetail.objects.all()
        resource_name = 'order_detail'
        allowed_methods = ['get', 'post', 'put', 'delete']
        always_return_data = True
        authorization = Authorization()  # THIS IS IMPORTANT
        filtering = {
            'order_header': ALL_WITH_RELATIONS,
        }
