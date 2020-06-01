import datetime
import logging

from django.conf.urls import url
from django.db.models import Sum
from django.http import JsonResponse
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash

from api.models.ads.room_ad import RoomAd

logger = logging.getLogger('api.room_ad_resource')


class RoomAdResource(ModelResource):

    class Meta:
        queryset = RoomAd.objects.all()
        resource_name = 'room_ad'
        object_class = RoomAd
        allowed_methods = ['get', 'post']
        authorization = Authorization()  # THIS IS IMPORTANT

    def prepend_urls(self):
        """ Add the following array of urls to the UserResource base urls """
        resource_name = self._meta.resource_name
        return [
            # update
            url(r"^(?P<resource_name>%s)/get_count%s$" %
                (resource_name, trailing_slash()),
                self.wrap_view('get_count'), name="api_get_count"),
            # ads reducer
            url(r"^(?P<resource_name>%s)/click_ads%s$" %
                (resource_name, trailing_slash()),
                self.wrap_view('reduce_ads'), name="api_click_ads")
        ]

    @staticmethod
    def get_count(request, **kwargs):
        room_id = request.GET.get('room_id', None)
        if room_id is None:
            return JsonResponse({
                'error': {
                    "message": "Room not found, please check again."
                }}, content_type='application/json', status=200)

        room = RoomAd.objects.all().filter(room_id=room_id, active=True,
                                           expired_date__gte=datetime.date.today()).aggregate(Sum('click'))
        logger.info('roomResource.update: room {}'.format(room))
        return JsonResponse({
            'click': room["click__sum"] or 0
        }, content_type='application/json', status=200)

    @staticmethod
    def reduce_ads(request, **kwargs):
        try:
            room_id = request.GET.get('room_id', None)
            if room_id is None:
                return JsonResponse({
                    'error': {
                        "message": "Room not found, please check again."
                    }}, content_type='application/json', status=500)

            room_ad = RoomAd.objects.filter(
                room_id=request.GET.get('room_id'),
                active=True,
                expired_date__gte=datetime.date.today(),
                start_date__lte=datetime.date.today(),
                click__gt=0
            ).order_by('expired_date', 'start_date').first()

            if room_ad is None:
                return JsonResponse({
                    'error': {
                        "message": "Room not found, please check again."
                    }}, content_type='application/json', status=500)
            room_ad.click -= 1
            if room_ad.click <= 0:
                room_ad.active = False
            room_ad.save()
            return JsonResponse({
                'objects': [{
                    "id": room_ad.id,
                    "click": room_ad.click,
                    'expired_date': room_ad.room_id
                }]
            }, content_type='application/json', status=200)
        except RoomAd.DoesNotExist:
            return JsonResponse({
                'error': {
                    "message": "Room doesn't have adsense, you can buy it first."
                }
            }, content_type='application/json', status=500)
        except Exception as e:
            logger.exception(e)
            return JsonResponse({
                'error': {
                    "message": str(e)
                }
            }, content_type='application/json', status=500)
