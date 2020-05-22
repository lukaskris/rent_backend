from tastypie.resources import ModelResource

# models
from api.models.room.feature import Feature


class FeaturesResource(ModelResource):
    class Meta:
        queryset = Feature.objects.all()
        resource_name = 'features'
