import uuid

from django.db import models


class CommissionPercentage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    percentage = models.DecimalField(max_digits=3, decimal_places=1)
