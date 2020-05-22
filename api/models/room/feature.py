import uuid

from django.db import models

from api.models.room.product import Product


# laundry cuci ac dll
class Feature(Product):
    feature_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
