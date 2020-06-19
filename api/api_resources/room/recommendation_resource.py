import datetime
import json
import logging

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.http import JsonResponse

# models
from api.models.ads.room_ad import RoomAd
from api.models.order.order_header import OrderHeader
from api.models.order.type_selling import TypeSelling
from api.models.room.room import Room
from api.models.room.room_detail import RoomDetail
from api.models.room.room_image import RoomImages

logger = logging.getLogger('api.recommendation')


def get_recommendation(self, request, **kwargs):
    try:
        order_header_set = OrderHeader.objects.filter(order_status_id__in=[1, 2]).values_list('product_id',
                                                                                              flat=True).annotate(
            product_id_count=Count('product_id')).order_by('-product_id')[:2]
        logger.info("Order header set: {}".format(order_header_set))
        valid_ads_list = RoomAd.objects.filter(expired_date__gte=datetime.datetime.now()).values_list('room_id',
                                                                                                      flat=True)[:5]
        logger.info("Value ads list: {}".format(valid_ads_list))

        ids = []
        if len(order_header_set) > 0:
            for data in order_header_set:
                ids.append(data)

        if len(valid_ads_list) > 0:
            for data in valid_ads_list:
                ids.append(data)
        logger.info("List of id: {}".format(ids))
        if len(ids) < 5:
            diff = 5 - len(ids)
            logger.info("DIFF: {}".format(diff))
            for id in Room.objects.all().exclude(product_id__in=ids).order_by('room_id').values_list(
                    'product_id',
                    flat=True)[
                      :diff]:
                ids.append(id)
            logger.info(ids)

        query = Room.objects.all().filter(product_id__in=ids, status=True) if len(ids) > 0 else Room.objects.filter(
            status=True).order_by('room_id')[:5]

        list_response = []
        for room in query:
            query_room_detail = RoomDetail.objects.filter(room_id=room.room_id).exclude(type_selling_id=4).values('id',
                                                                                                                  'room',
                                                                                                                  'price',
                                                                                                                  'type_selling')[:2]
            for roomDetail in query_room_detail:
                typeSelling = TypeSelling.objects.filter(id=roomDetail["type_selling"]).values('id', 'name')
                typeSellingSerialized = json.dumps(list(typeSelling), cls=DjangoJSONEncoder)
                roomDetail["type_selling"] = json.loads(typeSellingSerialized)[0]

            serializedQuery = json.dumps(list(query_room_detail), cls=DjangoJSONEncoder)
            roomDetails = json.loads(serializedQuery)

            queryImages = RoomImages.objects.filter(room_id=room.room_id).values('id', 'image', 'room')
            for image in queryImages:
                image["image"] = "/media/" + image["image"]
            serializedQuery = json.dumps(list(queryImages), cls=DjangoJSONEncoder)

            images = json.loads(serializedQuery)
            ads = False
            if room.room_id in valid_ads_list:
                ads = True
            if query_room_detail.exists():
                list_response.append({
                    'product_id': room.product_id,
                    'room_id': room.room_id,
                    'apartment_name': room.apartment.name,
                    'apartment_id': room.apartment.id,
                    'name': room.name,
                    'description': room.description,
                    'contact_person_name': room.contact_person_name,
                    'contact_person_phone': room.contact_person_phone,
                    'room_details': roomDetails,
                    'images': images,
                    'sqm_room': room.sqm_room,
                    'bedroom_total': room.bedroom_total,
                    'bathroom_total': room.bathroom_total,
                    'guest_maximum': room.guest_maximum,
                    'ads': ads
                })
            # logger.info(list_response)

        return JsonResponse({
            "objects": list_response
        }, content_type='application/json', status=200)

    except Exception as e:
        logger.exception(e)
        return JsonResponse({
            'error': {
                "message": str(e)
            }
        }, content_type='application/json', status=500)
