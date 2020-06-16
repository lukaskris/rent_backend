import uuid

from django.db import models


from api.models.user.user import User


class Product(models.Model):
    product_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, default="")
    description = models.TextField(default="")
    status = models.BooleanField(default=True)  # 0 1 active or not
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return self.name
