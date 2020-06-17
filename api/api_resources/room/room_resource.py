import json
import logging

from django.conf.urls import url
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.http import JsonResponse
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash

from api.api_resources.user_resource import UserResource
# models
from api.models.order.type_selling import TypeSelling
from api.models.room.room import Room
from api.models.room.room_detail import RoomDetail
from api.models.room.room_image import RoomImages
from .recommendation_resource import get_recommendation
from .room_detail_resource import RoomDetailResource
from .room_images_resource import RoomImagesResource
from .search_resource import search
from ..aparment.apartment_resource import ApartmentResource

logger = logging.getLogger('api.room_resource')


class RoomResource(ModelResource):
    created_by = fields.ToOneField(UserResource, attribute='created_by', full=True, null=False)
    room_details = fields.ToManyField(RoomDetailResource, 'room_detail', full=True, null=True)
    images = fields.ToManyField(RoomImagesResource, 'room_images', full=True, null=True)
    apartment = fields.ToOneField(ApartmentResource, 'apartment', full=True, null=True, )

    class Meta:
        queryset = Room.objects.filter(status=True)
        resource_name = 'room'
        allowed_methods = ['get', 'post', 'put', 'delete']
        always_return_data = True
        authorization = Authorization()  # THIS IS IMPORTANT
        filtering = {
            'room_id': ALL,
            'created_by': ALL_WITH_RELATIONS
        }

    def prepend_urls(self):
        """ Add the following array of urls to the UserResource base urls """
        resource_name = self._meta.resource_name
        return [
            # update
            url(r"^(?P<resource_name>%s)/update%s$" %
                (resource_name, trailing_slash()),
                self.wrap_view('update'), name="api_update"),
            # search
            url(r"^(?P<resource_name>%s)/search%s$" %
                (resource_name, trailing_slash()),
                self.wrap_view('search'), name="api_search"),
            # recommendation
            url(r"^(?P<resource_name>%s)/recommendation%s$" %
                (resource_name, trailing_slash()),
                self.wrap_view('recommendation'), name="api_recommendation")
        ]

    def search(self, request, **kwargs):
        return search(self=self, request=request)

    def recommendation(self, request, **kwargs):
        return get_recommendation(self, request)

    def update(self, request, **kwargs):

        # function for update products
        try:
            from django.http.multipartparser import MultiPartParser
            with transaction.atomic():
                logger.info("RoomResource.update: masuk")
                data = self.deserialize(
                    request, request.body,
                    format=request.content_type
                )

                logger.info('roomResource.update: Body {}'.format(data))

                roomId = data.get('room_id', "")
                productId = data.get('product_id', "")
                name = data.get('name', '')
                description = data.get('description', '')
                contactPersonName = data.get('contact_person_name', '')
                contactPersonPhone = data.get('contact_person_phone', '')
                roomDetails = data.get('room_details', [])
                roomImages = data.get('room_images', [])
                sqmRoom = data.get('sqm_room', 1)
                bedroomTotal = data.get('bedroom', 1)
                bathroomTotal = data.get('bathroom', 1)
                guestMaximum = data.get('guest_maximum', 1)
                apartment_id = data.get('apartment_id', 0)
                apartment_name = data.get('apartment_name', '')

                logger.info("RoomResource.update: {}".format(roomId))
                logger.info("RoomResource.update: {}".format("prepare update"))
                room = Room.objects.filter(pk=roomId)
                room.update(
                    name=name,
                    description=description,
                    contact_person_name=contactPersonName,
                    contact_person_phone=contactPersonPhone,
                    sqm_room=sqmRoom,
                    bedroom_total=bedroomTotal,
                    bathroom_total=bathroomTotal,
                    guest_maximum=guestMaximum,
                    apartment_id=apartment_id
                )

                for roomDetail in roomDetails:
                    price = roomDetail.get("price", '')
                    type_selling_id = roomDetail.get("type_selling_id")
                    logger.info("Loop room detail: {}".format(roomDetail))
                    try:
                        pd = RoomDetail.objects.get(room_id=roomId, type_selling_id=type_selling_id)
                        pd.price = price
                        pd.save()
                        logger.info("Update room detail: ")
                        logger.info(roomDetail)
                    except RoomDetail.DoesNotExist:
                        pd = RoomDetail.objects.create(
                            price=price,
                            type_selling_id=type_selling_id,
                            room_id=roomId
                        )
                        pd.save()
                        logger.info("Create room detail: ")
                        logger.info(roomDetail)
                roomDetailIds = list(map(lambda x: x.get("type_selling_id"), roomDetails))
                deletedRoomDetails = RoomDetail.objects.filter(room_id=roomId).exclude(type_selling_id__in=roomDetailIds)
                logger.info(deletedRoomDetails)
                for roomDetail in deletedRoomDetails:
                    roomDetail.delete()

                for roomImage in roomImages:
                    id = roomImage.get('id', -1)
                    RoomDetail.objects.filter(pk=id).delete()

                query_room_detail = RoomDetail.objects.filter(room_id=roomId).order_by('type_selling_id').values('id', 'room', 'price', 'type_selling')
                for roomDetail in query_room_detail:
                    typeSelling = TypeSelling.objects.filter(id=roomDetail["type_selling"]).values('id', 'name')
                    typeSellingSerialized = json.dumps(list(typeSelling), cls=DjangoJSONEncoder)
                    roomDetail["type_selling"] = json.loads(typeSellingSerialized)[0]

                serializedQuery = json.dumps(list(query_room_detail), cls=DjangoJSONEncoder)
                roomDetails = json.loads(serializedQuery)

                queryImages = RoomImages.objects.filter(room_id=roomId).values('id', 'image', 'room')
                for image in queryImages:
                    image["image"] = "/media/" + image["image"]
                serializedQuery = json.dumps(list(queryImages), cls=DjangoJSONEncoder)

                images = json.loads(serializedQuery)
                response = {
                    'product_id': productId,
                    'room_id': roomId,
                    'name': name,
                    'description': description,
                    'contact_person_name': contactPersonName,
                    'contact_person_phone': contactPersonPhone,
                    'room_details': roomDetails,
                    'images': images,
                    'sqm_room': sqmRoom,
                    'bedroom_total': bedroomTotal,
                    'bathroom_total': bathroomTotal,
                    'guest_maximum': guestMaximum,
                    'apartment_id': apartment_id,
                    'apartment_name': apartment_name,
                }
                logger.info(response)
                return JsonResponse(response, content_type='application/json', status=200)
        except Exception as e:
            logger.exception('roomResource.update onError: {}'.format(str(e)))
            return JsonResponse({
                'error': {
                    "message": str(e)
                }
            }, content_type='application/json', status=500)
