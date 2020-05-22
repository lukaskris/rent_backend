import datetime

from django.conf.urls import url
from django.db.models import Sum
from django.http import JsonResponse
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash

from api.models.ads.room_ad import RoomAd
from api.api_resources.room.room_resource import RoomResource


def get_count(request):
    room = RoomAd.objects.all().filter(room_id=request.GET.get('room_id'), active=True,
                                       expired_date__gte=datetime.date.today()).aggregate(Sum('click'))
    print('roomResource.update: room {}'.format(room))
    return JsonResponse({
        'click': room["click__sum"]
    }, content_type='application/json', status=200)


class RoomAdResource(ModelResource):
    room = fields.ToOneField(RoomResource, 'room')

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
                self.wrap_view('get_count'), name="api_get_count")
        ]
