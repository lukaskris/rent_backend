from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource

from api.api_resources.helper.multipart_request import MultipartResource
# models
from api.models.room.room_image import RoomImages


class RoomImagesResource(MultipartResource, ModelResource):
    room = fields.ToOneField('api.api_resources.room.room_resource.RoomResource', 'room')

    class Meta:
        queryset = RoomImages.objects.all()
        resource_name = 'room_images'
        allowed_methods = ['get', 'post', 'patch', 'delete']
        authorization = Authorization()
        always_return_data = True
