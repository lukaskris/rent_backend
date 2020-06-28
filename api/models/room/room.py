import uuid

from django.db import models

from api.models.apartment.apartment import Apartment
from api.models.apartment.tower import Tower
from api.models.room.product import Product


class Room(Product):
    room_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bedroom_total = models.IntegerField(default=1)
    guest_maximum = models.IntegerField(default=1)
    bathroom_total = models.IntegerField(default=1)
    sqm_room = models.IntegerField(default=24)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    apartment = models.ForeignKey(Apartment, on_delete=models.DO_NOTHING, null=True)
    tower = models.ForeignKey(Tower, on_delete=models.DO_NOTHING, null=True)
    contact_person_name = models.CharField(max_length=200, default="")
    contact_person_phone = models.CharField(max_length=200, default="")
