from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource

from api.models.order.type_selling import TypeSelling


class TypeSellingResource(ModelResource):
    room_detail = fields.ToManyField('api.api_resources.room.room_detail_resource.RoomDetailResource', 'room_detail_set', related_name='type_selling',
                                     null=True)

    class Meta:
        queryset = TypeSelling.objects.all()
        resource_name = 'type_selling'
        authorization = Authorization()
