import uuid

from django.db import models

# ads bundle
from api.models.room.product import Product


class AdsBundle(Product):
    ads_bundle_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_click = models.IntegerField()
