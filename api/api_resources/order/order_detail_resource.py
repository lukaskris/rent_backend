from tastypie.authentication import ApiKeyAuthentication
from tastypie.resources import ModelResource

from api.models.order.order_detail import OrderDetail


class OrderDetailResource(ModelResource):
    class Meta:
        queryset = OrderDetail.objects.all()
        resource_name = 'order_detail'
        authentication = ApiKeyAuthentication()
