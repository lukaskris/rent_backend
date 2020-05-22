from django.db import models


# Type Penjualan
# 1 sewa harian, 2 sewa mingguan ..., 5 jual
class TypeSelling(models.Model):
    name = models.TextField()
