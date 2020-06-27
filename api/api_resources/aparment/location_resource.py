from tastypie.authorization import Authorization
from tastypie.constants import ALL
from tastypie.resources import ModelResource

from api.models.location.location import Location


class LocationResource(ModelResource):
    class Meta:
        queryset = Location.objects.filter(active=True)
        resource_name = 'location'
        always_return_data = True
        list_allowed_methods = ['get', 'post', 'put']
        authorization = Authorization()
        filtering = {
            'id': ALL
        }
