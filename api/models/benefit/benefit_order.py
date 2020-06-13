import uuid

from django.db import models

from api.models.order.order_header import OrderHeader
from api.models.user.user import User


class BenefitOrder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    order = models.ForeignKey(OrderHeader, on_delete=models.DO_NOTHING)
    nominal = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
