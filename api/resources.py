from tastypie.resources import ModelResource
from api.models import Users

class UserResource(ModelResource):
    class Meta:
        queryset = Users.objects.all()
        resource_name = 'user'
