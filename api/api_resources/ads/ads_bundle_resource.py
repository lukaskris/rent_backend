from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource

from api.models.ads.ad_bundle import AdsBundle
from api.api_resources.user_resource import UserResource


class AdsBundleResource(ModelResource):
    created_by = fields.ToOneField(UserResource, attribute='created_by', full=True, null=False)

    class Meta:
        queryset = AdsBundle.objects.all()
        allowed_methods = ['get', 'post', 'put', 'delete']
        authorization = Authorization()  # THIS IS IMPORTANT
        resource_name = 'ads_bundle'
        always_return_data = True
