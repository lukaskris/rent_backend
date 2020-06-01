from django.db import models


from api.models.order.order_header import OrderHeader
from api.models.room.feature import Feature


class OrderDetail(models.Model):
    order_header = models.ForeignKey(OrderHeader, on_delete=models.PROTECT)
    feature = models.ForeignKey(Feature, on_delete=models.DO_NOTHING)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __unicode__(self):
        return self.order_header, self.price
