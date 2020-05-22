from django.db import models

from api.helper.path_and_rename import PathAndRename


class Banner(models.Model):
    image = models.FileField(upload_to=PathAndRename("images/banners/"), verbose_name='Banner')
    active_at = models.DateTimeField(auto_now_add=False)
    expired_at = models.DateTimeField(auto_now_add=False)
