
import logging

from django.utils.datetime_safe import datetime

from api.models.ads.room_ad import RoomAd

from apscheduler.schedulers.background import BackgroundScheduler

from api.models.order.order_header import OrderHeader

logger = logging.getLogger('api.cronjob.expired_transaction')


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(expired_transaction, 'interval', minutes=1)
    scheduler.start()


def expired_transaction():
    try:
        # checking payment type is null
        OrderHeader.objects.filter(
            active=True,
            expired_date__lte=datetime.now(),
            payment_type=None
        ).update(active=False, order_status_id=3)
        print("Updating order header when payment is null")

        # checking expired
        OrderHeader.objects.filter(
            active=True,
            expired_date__lte=datetime.now(),
            order_status_id=1
        ).update(active=False, order_status_id=3)
        print("Updating order header when expired")

        # checking room ad is expired
        RoomAd.objects.filter(
            active=True,
            expired_date__lte=datetime.now()
        ).update(active=False)
        print("Updating room ads when expired")
    except Exception as e:
        logger.exception(e)
        pass
