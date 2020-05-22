from tastypie.authorization import Authorization
from tastypie.resources import ModelResource

from api.models.apartment.apartment import Apartment


class ApartmentResource(ModelResource):
    class Meta:
        queryset = Apartment.objects.all()
        resource_name = 'apartment'
        always_return_data = True
        authorization = Authorization()
