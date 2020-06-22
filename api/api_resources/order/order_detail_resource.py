from tastypie.authorization import Authorization
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.resources import ModelResource

from api.models.order.order_detail import OrderDetail


class OrderDetailResource(ModelResource):
    class Meta:
        queryset = OrderDetail.objects.all()
        resource_name = 'order_detail'
        allowed_methods = ['get', 'post', 'put', 'delete']
        always_return_data = True
        authorization = Authorization()  # THIS IS IMPORTANT
        filtering = {
            'order_header': ALL_WITH_RELATIONS,
        }
