from django.db import models

from api.helper.path_and_rename import PathAndRename
from api.models.room.room import Room


class RoomImages(models.Model):
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='room_images', blank=True, null=True)
    image = models.FileField(upload_to=PathAndRename("images/products/"), verbose_name='Room')
