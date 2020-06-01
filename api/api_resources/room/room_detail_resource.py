from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.resources import ModelResource

# models
from api.api_resources.order.type_selling import TypeSellingResource
from api.api_resources.room.room_resource import RoomResource
from api.models.room.room_detail import RoomDetail


class RoomDetailResource(ModelResource):
    room = fields.ToOneField(RoomResource, 'room_details', full=True, null=True)
    type_selling = fields.ToOneField(TypeSellingResource, 'type_selling', full=True, null=True)

    class Meta:
        queryset = RoomDetail.objects.exclude(type_selling_id=4)
        resource_name = 'room_detail'
        allowed_methods = ['get', 'post', 'put']
        authorization = Authorization()
        always_return_data = True
        filtering = {
            'room': ALL_WITH_RELATIONS,
        }
