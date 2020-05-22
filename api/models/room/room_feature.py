from django.db import models

from api.models.room.feature import Feature
from api.models.room.room_detail import RoomDetail


class RoomFeature(models.Model):
    feature = models.ForeignKey(Feature, on_delete=models.DO_NOTHING)
    room_detail = models.ForeignKey(RoomDetail, on_delete=models.DO_NOTHING)
    price = models.DecimalField(max_digits=10, decimal_places=2)

