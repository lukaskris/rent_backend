from django.db import models

from api.models.order.type_selling import TypeSelling
from api.models.room.room import Room


class RoomDetail(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room_detail', blank=True, null=True)
    type_selling = models.ForeignKey(TypeSelling, on_delete=models.DO_NOTHING)
    price = models.DecimalField(max_digits=12, decimal_places=2)
