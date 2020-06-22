import uuid

from django.db import models

from api.models.room.product import Product


# ac cleaning dan room cleaning
class Feature(Product):
    feature_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
