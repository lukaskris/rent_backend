import logging

from django.conf.urls import url
from django.db import transaction
from django.http import JsonResponse
from fcm_django.models import FCMDevice
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource

# models
from api.models.benefit.benefit_order import BenefitOrder
from api.models.benefit.benefit_staff import BalanceStaff, BalanceHistory
from api.models.benefit.commission_percentage import CommissionPercentage
from api.models.notification.notifiaction import Notification
from api.models.order.order_header import OrderHeader

logger = logging.getLogger('api.notification')


class NotificationResource(ModelResource):
    class Meta:
        queryset = Notification.objects.all()
        resource_name = 'notification'
        authorization = Authorization()

    def prepend_urls(self):
        """ Add the following array of urls to the UserResource base urls """
        resource_name = self._meta.resource_name
        return [
            # update
            url(r"^(?P<resource_name>%s)/handling/$" %
                resource_name,
                self.wrap_view('handling'), name="api_handling")
        ]

    def handling(self, request, **kwargs):
        try:
            with transaction.atomic():
                logger.info("NotificationResource.handling: masuk")
                data = self.deserialize(
                    request, request.body,
                    format=request.content_type
                )

                logger.info('NotificationResource.handling: Body {}'.format(data))

                midtrans_id = data.get("order_id", "")
                payment_type = data.get("payment_type", "")
                transaction_status = data.get("transaction_status", "")

                payment_number = ""
                transaction_type = ""
                order_status_id = 1
                message_notification = ""

                if payment_type == "bank_transfer" and "permata_va_number" in data.keys():
                    transaction_type = "permata"
                    payment_number = data.get("permata_va_number", '')
                elif payment_type == "bank_transfer" and "va_numbers" in data.keys():
                    va = data.get('va_numbers')
                    payment_number = va[0].get('va_number', '')
                    transaction_type = va[0].get('bank', '')
                elif payment_type == "bank_transfer" and "bill_key" in data.keys():
                    bill_key = data.get('bill_key', '')
                    payment_number = bill_key
                    transaction_type = 'mandiri'
                elif payment_type == "bca_klikpay" or payment_type == 'bca_klikbca':
                    transaction_type = payment_type
                    if "approval_code" in data.keys():
                        payment_number = data.get('approval_code', '')
                elif payment_type == "cstore":
                    transaction_type = data.get('store', '')
                    payment_number = data.get('payment_code', '')

                if transaction_status == "pending":
                    message_notification = "Transaksi sedang menunggu pembayaran!."
                    order_status_id = 1
                elif transaction_status == "settlement":
                    message_notification = "Pembayaran berhasil di verifikasi"
                    order_status_id = 2
                elif transaction_status == "expire" or transaction_status == "cancel":
                    message_notification = "Pembayaran telah lewat waktu yang ditentukan"
                    order_status_id = 3

                order_header = OrderHeader.objects.get(midtrans_id=midtrans_id)
                order_header.payment_number = payment_number
                order_header.payment_type = transaction_type
                order_header.order_status_id = order_status_id
                order_header.save()
                logger.info("Order header saved {}".format(order_header))
                if transaction_status == "settlement":
                    try:
                        balance_staff = BalanceStaff.objects.get(user=order_header.product.created_by)
                    except BalanceStaff.DoesNotExist:
                        balance_staff = BalanceStaff.objects.create(user=order_header.product.created_by)

                    percentage = CommissionPercentage.objects.first().percentage

                    commission = order_header.grand_total * (percentage / 100)

                    balance_staff.balance = balance_staff.balance + commission
                    balance_staff.save()
                    benefit_order = BenefitOrder.objects.create(
                        user=order_header.product.created_by,
                        order=order_header,
                        nominal=commission
                    )
                    BalanceHistory.objects.create(
                        user=order_header.product.created_by,
                        benefit_order=benefit_order,
                        nominal=commission
                    )

                    Notification.objects.create(
                        user_id=order_header.user_id,
                        message=message_notification,
                        order_header_id=order_header.id
                    )
                    logger.info("Notification saved")
                    try:
                        device = FCMDevice.objects.filter(user_id=order_header.user_id)
                        logger.info("Device get {}".format(device))
                        logger.info("Order header type selling {}".format(order_header.type_selling_id))
                        message_data = {
                            "order_header_id": str(order_header.id),
                            "type": "Ad" if order_header.type_selling_id is None else "Room"
                        }
                        logger.info("Message data {}".format(message_data))
                        device.send_message(title="Pembayaran", body=message_notification, data=message_data)
                    except Exception as e:
                        print(e)

                    device2 = FCMDevice.objects.filter(user_id=order_header.product.created_by.id)
                    logger.info("Message data {}".format(message_data))
                    price_formatted = "IDR {:,.0f}".format(commission)
                    device2.send_message(title="Komisi", body="Kamu mendapatkan komisi penyewaan apartemen {}".format(price_formatted), data=[])

                return JsonResponse({
                    'success': {
                        "message": "true"
                    }
                }, content_type='application/json', status=200)
        except Exception as e:
            logger.exception('roomResource.update onError: {}'.format(str(e)))
            return JsonResponse({
                'error': {
                    "message": str(e)
                }
            }, content_type='application/json', status=500)
