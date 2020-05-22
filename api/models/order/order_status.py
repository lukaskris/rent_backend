from django.db import models


# Status order
# 1. Need Payment
# 2. Payment Success
# 3. Payment Fail
# 4.
class OrderStatus(models.Model):
    name = models.TextField()
