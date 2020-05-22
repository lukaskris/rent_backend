from tastypie.resources import ModelResource

from api.models.order.order_status import OrderStatus


class OrderStatusResource(ModelResource):
    class Meta:
        queryset = OrderStatus.objects.all()
        resource_name = 'order_status'
