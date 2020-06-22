from tastypie.authorization import Authorization
from tastypie.constants import ALL
from tastypie.resources import ModelResource

# models
from api.models.room.feature import Feature


class FeaturesResource(ModelResource):
    class Meta:
        queryset = Feature.objects.all()
        resource_name = 'features'
        authorization = Authorization()
        always_return_data = True
        allowed_methods = ['get', 'post', 'put']
        filtering = {
            'status': ALL
        }