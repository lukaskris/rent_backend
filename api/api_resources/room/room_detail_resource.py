from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.resources import ModelResource

# models
from api.models.room.room_detail import RoomDetail
from api.api_resources.room.room_resource import RoomResource


class RoomDetailResource(ModelResource):
    room = fields.ToOneField(RoomResource, 'room')
    type_selling = fields.ToOneField('api.api_resources.TypeSellingResource', 'type_selling', full=True, null=False)

    class Meta:
        queryset = RoomDetail.objects.all()
        resource_name = 'room_detail'
        allowed_methods = ['get', 'post', 'put', 'delete']
        authorization = Authorization()
        always_return_data = True
        filtering = {
            'room': ALL_WITH_RELATIONS,
        }
