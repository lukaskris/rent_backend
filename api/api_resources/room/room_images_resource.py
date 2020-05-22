from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource

# models
from api.models.room.room_image import RoomImages
from api.api_resources.helper.multipart_request import MultipartResource


class RoomImagesResource(MultipartResource, ModelResource):
    room = fields.ToOneField('api.api_resources.RoomResource', 'room')

    class Meta:
        queryset = RoomImages.objects.all()
        resource_name = 'room_images'
        allowed_methods = ['get', 'post', 'delete']
        authorization = Authorization()
        always_return_data = True
