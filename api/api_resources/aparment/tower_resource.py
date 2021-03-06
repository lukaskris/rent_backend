from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL
from tastypie.resources import ModelResource

from api.models.apartment.tower import Tower


class TowerResource(ModelResource):
    apartment = fields.ToOneField('api.api_resources.aparment.apartment_resource.ApartmentResource', 'apartment',
                                  null=True)

    class Meta:
        queryset = Tower.objects.filter(active=True)
        resource_name = 'tower'
        always_return_data = True
        list_allowed_methods = ['get', 'post', 'put']
        authorization = Authorization()
        filtering = {
            'id': ALL,
            'name': ALL
        }
