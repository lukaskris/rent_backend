import uuid

from django.db import models
from django.utils import timezone

from api.models.order.order_status import OrderStatus
from api.models.order.type_selling import TypeSelling

# Payments header
from api.models.room.product import Product
from api.models.user.user import User


def auto_increment_invoice():
    import datetime as date
    monthFormat = str(date.date.today().month)
    currentFormat = "SE/" + str(date.date.today().year) + "/" + (2 - len(monthFormat)) * "0" + monthFormat + "/"
    try:
        order_header = OrderHeader.objects.all().order_by('order_date').last()
        # "SE/2020/04/00001"
        if not order_header:
            return currentFormat + "00001"
        formatSplit = order_header.invoice_ref_number.split('/')

        if formatSplit[1] != str(date.date.today().year) and formatSplit[2] != str(date.date.today().month):
            return currentFormat + "00001"

        invoice_no = order_header.invoice_ref_number
        invoice_int = int(invoice_no.split(currentFormat)[-1])
        new_invoice_int = invoice_int + 1
        width = 5
        formatted = (width - len(str(new_invoice_int))) * "0" + str(new_invoice_int)
        new_invoice_no = currentFormat + str(formatted)
        return new_invoice_no
    except Exception as e:
        return currentFormat + "00001"


class OrderHeader(models.Model):
    class Meta:
        unique_together = [['id', 'midtrans_id', 'invoice_ref_number']]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    midtrans_id = models.TextField(default="")
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    type_selling = models.ForeignKey(TypeSelling, on_delete=models.DO_NOTHING, default=None, blank=None, null=True)
    invoice_ref_number = models.CharField(max_length=500, default=auto_increment_invoice, null=True, blank=True)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    order_date = models.DateTimeField(auto_now_add=True)
    expired_date = models.DateTimeField(null=True)
    payment_date = models.DateTimeField()
    order_status = models.ForeignKey(OrderStatus, on_delete=models.DO_NOTHING)
    payment_type = models.TextField(null=True)
    payment_number = models.TextField(null=True)
    check_in_time = models.DateTimeField()
    check_out_time = models.DateTimeField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.invoice_ref_number
