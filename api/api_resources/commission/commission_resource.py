from tastypie.authorization import Authorization
from tastypie.resources import ModelResource

from api.models.apartment.apartment import Apartment
from api.models.benefit.commission_percentage import CommissionPercentage


class CommissionResource(ModelResource):
    class Meta:
        queryset = CommissionPercentage.objects.all()
        resource_name = 'commission'
        always_return_data = True
        authorization = Authorization()
