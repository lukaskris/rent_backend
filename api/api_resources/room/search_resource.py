import json
import logging
from operator import itemgetter

from django.core.serializers.json import DjangoJSONEncoder
from django.db import connection
from django.http import JsonResponse

# models
from api.api_resources.query.search_query import SearchQuery
from api.models.apartment.tower import Tower
from api.models.room.room_image import RoomImages

logger = logging.getLogger('api.search')

product_id = 0
room_id = 1
name = 2
description = 3
price = 4
bedroom_total = 5
guest_maximum = 6
bathroom_total = 7
sqm_room = 8
rating = 9
contact_person_name = 10
contact_person_phone = 11
apartment_id = 12
apartment_name = 13
type_selling_id = 14
type_selling_name = 15
room_detail_id = 16
tower_id = 18
ad = 19


def search(self, request):
    try:
        sort = request.GET.get('sort', '1')
        filter = int(request.GET.get('filter', 0))
        tower = int(request.GET.get('tower', 0))
        offset = int(request.GET.get('offset', 0))
        type_selling = int(request.GET.get('type_selling_id', 1))
        check_in = request.GET.get('check_in')
        check_out = request.GET.get('check_out')

        query_ads = SearchQuery.ads_query(order_by=sort, offset=offset / 10, check_in=check_in,
                                          check_out=check_out, type_booking=type_selling, filter_by=filter, tower=tower)
        query = SearchQuery.non_ads_query(order_by=sort, offset=offset / 10, check_in=check_in,
                                          check_out=check_out, type_booking=type_selling, filter_by=filter, tower=tower)

        cursor = connection.cursor()

        cursor.execute(query)
        non_ads = cursor.fetchall()

        cursor.execute(query_ads)
        ads = cursor.fetchall()

        list_response = []

        rooms = ads + non_ads

        if sort == "2" or sort == "3":
            rooms = sorted(rooms, key=itemgetter(4), reverse=sort == "3")

        for room in rooms:
            queryImages = RoomImages.objects.filter(room_id=room[1]).values('id', 'image', 'room')
            tower = Tower.objects.get(id=int(room[tower_id]))
            for image in queryImages:
                image["image"] = "/media/" + image["image"]
            serializedQuery = json.dumps(list(queryImages), cls=DjangoJSONEncoder)

            images = json.loads(serializedQuery)
            list_response.append({
                'product_id': room[product_id],
                'room_id': room[room_id],
                'name': room[name],
                'description': room[description],
                'contact_person_name': room[contact_person_name],
                'contact_person_phone': room[contact_person_phone],
                'apartment_id': room[apartment_id],
                'apartment_name': room[apartment_name],
                'room_details': [
                    {
                        'price': room[price],
                        'type_selling': {
                            'id': room[type_selling_id],
                            'name': room[type_selling_name]
                        },
                        'id': room[room_detail_id]
                    }
                ],
                'images': images,
                'sqm_room': room[sqm_room],
                'bedroom_total': room[bedroom_total],
                'bathroom_total': room[bathroom_total],
                'guest_maximum': room[guest_maximum],
                'rating': room[rating],
                'tower': {
                    'name': tower.name,
                    'active': tower.active,
                    'id': tower.id
                },
                'ads': room[ad]
            })

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
