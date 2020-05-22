import uuid

from django.db import models

from api.models.order.order_header import OrderHeader
from api.models.user.user import User


class Notification(models.Model):
    notification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    message = models.TextField(default="")
    order_header = models.ForeignKey(OrderHeader, on_delete=models.DO_NOTHING, default=None, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
