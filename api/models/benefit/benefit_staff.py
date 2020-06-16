import uuid

from django.db import models

from api.models.benefit.benefit_order import BenefitOrder
from api.models.user.user import User


class BalanceStaff(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class BalanceHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    benefit_order = models.ForeignKey(BenefitOrder, on_delete=models.DO_NOTHING, null=True)
    nominal = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
