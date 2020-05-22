from django.db import models

from api.models.room.room import Room


class RoomAd(models.Model):
    room = models.ForeignKey(Room, on_delete=models.PROTECT)
    click = models.IntegerField(default=0)  # 10x click
    expired_date = models.DateTimeField()
    start_date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
