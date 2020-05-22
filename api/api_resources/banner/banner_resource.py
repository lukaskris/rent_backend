from tastypie.authorization import Authorization
from tastypie.constants import ALL
from tastypie.resources import ModelResource

from api.models.banner.banner import Banner


class BannerResource(ModelResource):
    class Meta:
        queryset = Banner.objects.all()
        resource_name = 'banner'
        allowed_methods = ['get']
        always_return_data = True
        authorization = Authorization()
        filtering = {
            'active_at': ALL,
            'expired_at': ALL
        }