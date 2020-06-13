from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.resources import ModelResource

from api.api_resources.user_resource import UserResource
from api.models.benefit.benefit_staff import BalanceStaff


class BalanceUserResource(ModelResource):
    user = fields.ToOneField(UserResource, attribute='user', full=True, null=True)

    class Meta:
        queryset = BalanceStaff.objects.all()
        resource_name = 'balance'
        filtering = {
            'user': ALL_WITH_RELATIONS
        }
        authorization = Authorization()
