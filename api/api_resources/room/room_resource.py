import datetime
import json
from datetime import datetime as dtime
from operator import itemgetter

from django.conf.urls import url
from django.core.serializers.json import DjangoJSONEncoder
from django.db import connection
from django.db.models import Count
from django.http import JsonResponse
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash

# models
from api.models.ads.room_ad import RoomAd
from api.models.order.order_header import OrderHeader
from api.models.order.type_selling import TypeSelling
from api.models.room.room import Room
from api.models.room.room_detail import RoomDetail
from api.models.room.room_image import RoomImages
from api.api_resources.user_resource import UserResource


def search(request):
    try:
        check_in_time = dtime.strptime(request.GET.get('check_in'), '%d%m%Y')
        check_out_time = dtime.strptime(request.GET.get('check_out'), '%d%m%Y')
        sort = request.GET.get('sort', '1')
        filter = int(request.GET.get('filter', 0))
        offset = int(request.GET.get('offset', 0))
        type_selling_id = request.GET.get('type_selling_id', '1')
        check_in = request.GET.get('check_in')
        check_out = request.GET.get('check_out')

        order_header_set = OrderHeader.objects.values_list('product_id', flat=True).filter(
            check_in_time=check_in_time, check_out_time=check_out_time, type_selling__isnull=False,
            order_status_id__in=[1, 2])
        print("ORDER HEADER SET " % order_header_set)

        valid_ads_list = RoomAd.objects.filter(expired_date__gte=datetime.datetime.now()).values_list('room_id', flat=True)[offset:2]
        print("VALUE VALID ADS: " % valid_ads_list)
        query_filter = "and apartment_id = %d" % filter
        print(query_filter)
        if sort == "1":
            query = '''
                SELECT product_id, ar.room_id, tblOrder.name, description, price, bedroom_total, guest_maximum, bathroom_total, sqm_room, rating, contact_person_name, contact_person_phone, apartment_id, type_selling_id, ard.id as room_detail_id, false as Ad, aprt."name" as apartment_name, aty.name as type_selling_name
                FROM (
                        SELECT count(ao.product_id) as total, ap.product_id, ap."name", ap.description
                        FROM api_product ap
                        JOIN api_orderheader ao
                        ON ap.product_id = ao.product_id and (ao.check_in_time not BETWEEN to_date('%s','ddMMyyyy') and to_date('%s','ddMMyyyy'))
                            and (ao.check_out_time not BETWEEN to_date('%s','ddMMyyyy') and to_date('%s','ddMMyyyy')) and ao.order_status_id != 3 and (ao.payment_type is not null or ao.payment_type != '' or (order_status_id = 1 and expired_date >= now()))
                        GROUP BY ap.product_id
                        ORDER BY count(ao.product_id) desc
                    ) tblOrder, api_room ar, api_roomdetail ard, api_apartment aprt, api_typeselling aty
                WHERE tblOrder.product_id = ar.product_ptr_id and ar.room_id = ard.room_id and ard.type_selling_id = '%s' and aprt.id = apartment_id
                and ar.room_id not in (SELECT room_id from api_roomad where start_date <= now() and expired_date >= now()) and aty.id = %s
                %s
                OFFSET %d
                LIMIT 10
            ''' % (check_in, check_in, check_out, check_out, type_selling_id, type_selling_id,
                   query_filter if (filter != 0) else '', offset)

            query_ads = '''
                SELECT product_id, ar.room_id, tblOrder.name, description, price, bedroom_total, guest_maximum, bathroom_total, sqm_room, rating, contact_person_name, contact_person_phone, apartment_id, type_selling_id, ard.id as room_detail_id, true as Ad, aprt."name" as apartment_name, aty.name as type_selling_name
                FROM (
                        SELECT count(ao.product_id) as total, ap.product_id, ap."name", ap.description
                        FROM api_product ap
                        JOIN api_orderheader ao
                        ON ap.product_id = ao.product_id and (ao.check_in_time not BETWEEN to_date('%s','ddMMyyyy') and to_date('%s','ddMMyyyy'))
                            and (ao.check_out_time not BETWEEN to_date('%s','ddMMyyyy') and to_date('%s','ddMMyyyy')) and ao.order_status_id != 3 and (ao.payment_type is not null or ao.payment_type != '' or (order_status_id = 1 and expired_date >= now()))
                        GROUP BY ap.product_id
                        ORDER BY count(ao.product_id) desc
                    ) tblOrder, api_room ar, api_roomdetail ard, api_apartment aprt, api_typeselling aty
                WHERE tblOrder.product_id = ar.product_ptr_id and ar.room_id = ard.room_id and ard.type_selling_id = '%s' and aprt.id = apartment_id
                and ar.room_id in (SELECT room_id from api_roomad where start_date <= now() and expired_date >= now()) and aty.id = %s
                %s
                OFFSET %d
                LIMIT 10
            ''' % (check_in, check_in, check_out, check_out, type_selling_id, type_selling_id,
                   query_filter if (filter != 0) else '', offset / 10)
        elif sort == "2":
            query = '''
                SELECT product_id, ar.room_id, tblOrder.name, description, price, bedroom_total, guest_maximum, bathroom_total, sqm_room, rating, contact_person_name, contact_person_phone, apartment_id, type_selling_id, ard.id as room_detail_id, false as Ad, aprt."name" as apartment_name, aty.name as type_selling_name
                FROM (
                        SELECT count(ao.product_id) as total, ap.product_id, ap."name", ap.description
                        FROM api_product ap
                        JOIN api_orderheader ao
                        ON ap.product_id = ao.product_id and (ao.check_in_time not BETWEEN to_date('%s','ddMMyyyy') and to_date('%s','ddMMyyyy'))
                            and (ao.check_out_time not BETWEEN to_date('%s','ddMMyyyy') and to_date('%s','ddMMyyyy')) and ao.order_status_id != 3 and (ao.payment_type is not null or ao.payment_type != '' or (order_status_id = 1 and expired_date >= now()))
                        GROUP BY ap.product_id
                        ORDER BY count(ao.product_id) desc
                    ) tblOrder, api_room ar, api_roomdetail ard, api_apartment aprt, api_typeselling aty
                WHERE tblOrder.product_id = ar.product_ptr_id and ar.room_id = ard.room_id and ard.type_selling_id = '%s' and aprt.id = apartment_id
                and ar.room_id not in (SELECT room_id from api_roomad where start_date <= now() and expired_date >= now()) and aty.id = %s
                %s
                ORDER BY price
                OFFSET %d
                LIMIT 10
            ''' % (check_in, check_in, check_out, check_out, type_selling_id, type_selling_id,
                   query_filter if (filter != 0) else '', offset)

            query_ads = '''
                SELECT product_id, ar.room_id, tblOrder.name, description, price, bedroom_total, guest_maximum, bathroom_total, sqm_room, rating, contact_person_name, contact_person_phone, apartment_id, type_selling_id, ard.id as room_detail_id, true as Ad, aprt."name" as apartment_name, aty.name as type_selling_name
                FROM (
                        SELECT count(ao.product_id) as total, ap.product_id, ap."name", ap.description
                        FROM api_product ap
                        JOIN api_orderheader ao
                        ON ap.product_id = ao.product_id and (ao.check_in_time not BETWEEN to_date('%s','ddMMyyyy') and to_date('%s','ddMMyyyy'))
                            and (ao.check_out_time not BETWEEN to_date('%s','ddMMyyyy') and to_date('%s','ddMMyyyy')) and ao.order_status_id != 3 and (ao.payment_type is not null or ao.payment_type != '' or (order_status_id = 1 and expired_date >= now()))
                        GROUP BY ap.product_id
                        ORDER BY count(ao.product_id) desc
                    ) tblOrder, api_room ar, api_roomdetail ard, api_apartment aprt, api_typeselling aty
                WHERE tblOrder.product_id = ar.product_ptr_id and ar.room_id = ard.room_id and ard.type_selling_id = '%s' and aprt.id = apartment_id
                and ar.room_id in (SELECT room_id from api_roomad where start_date <= now() and expired_date >= now()) and aty.id = %s
                %s
                ORDER BY price
                OFFSET %d
                LIMIT 10
            ''' % (check_in, check_in, check_out, check_out, type_selling_id, type_selling_id,
                   query_filter if (filter != 0) else '', offset / 10)
        else:
            query = '''
                SELECT product_id, ar.room_id, tblOrder.name, description, price, bedroom_total, guest_maximum, bathroom_total, sqm_room, rating, contact_person_name, contact_person_phone, apartment_id, type_selling_id, ard.id as room_detail_id, false as Ad, aprt."name" as apartment_name, aty.name as type_selling_name
                FROM (
                        SELECT count(ao.product_id) as total, ap.product_id, ap."name", ap.description
                        FROM api_product ap
                        JOIN api_orderheader ao
                        ON ap.product_id = ao.product_id and (ao.check_in_time not BETWEEN to_date('%s','ddMMyyyy') and to_date('%s','ddMMyyyy'))
                            and (ao.check_out_time not BETWEEN to_date('%s','ddMMyyyy') and to_date('%s','ddMMyyyy')) and ao.order_status_id != 3 and (ao.payment_type is not null or ao.payment_type != '' or (order_status_id = 1 and expired_date >= now()))
                        GROUP BY ap.product_id
                        ORDER BY count(ao.product_id) desc
                    ) tblOrder, api_room ar, api_roomdetail ard, api_apartment aprt, api_typeselling aty
                WHERE tblOrder.product_id = ar.product_ptr_id and ar.room_id = ard.room_id and ard.type_selling_id = '%s' and aprt.id = apartment_id
                and ar.room_id not in (SELECT room_id from api_roomad where start_date <= now() and expired_date >= now()) and aty.id = %s
                %s
                ORDER BY price desc
                OFFSET %d
                LIMIT 10
            ''' % (check_in, check_in, check_out, check_out, type_selling_id, type_selling_id,
                   query_filter if (filter != 0) else '', offset)

            query_ads = '''
                SELECT product_id, ar.room_id, tblOrder.name, description, price, bedroom_total, guest_maximum, bathroom_total, sqm_room, rating, contact_person_name, contact_person_phone, apartment_id, type_selling_id, ard.id as room_detail_id, true as Ad, aprt."name" as apartment_name, aty.name as type_selling_name
                FROM (
                        SELECT count(ao.product_id) as total, ap.product_id, ap."name", ap.description
                        FROM api_product ap
                        JOIN api_orderheader ao
                        ON ap.product_id = ao.product_id and (ao.check_in_time not BETWEEN to_date('%s','ddMMyyyy') and to_date('%s','ddMMyyyy'))
                            and (ao.check_out_time not BETWEEN to_date('%s','ddMMyyyy') and to_date('%s','ddMMyyyy')) and ao.order_status_id != 3 and (ao.payment_type is not null or ao.payment_type != '' or (order_status_id = 1 and expired_date >= now()))
                        GROUP BY ap.product_id
                        ORDER BY count(ao.product_id) desc
                    ) tblOrder, api_room ar, api_roomdetail ard, api_apartment aprt, api_typeselling aty
                WHERE tblOrder.product_id = ar.product_ptr_id and ar.room_id = ard.room_id and ard.type_selling_id = '%s' and aprt.id = apartment_id
                and ar.room_id in (SELECT room_id from api_roomad where start_date <= now() and expired_date >= now()) and aty.id = %s
                %s
                ORDER BY price desc
                OFFSET %d
                LIMIT 10
            ''' % (check_in, check_in, check_out, check_out, type_selling_id, type_selling_id,
                   query_filter if (filter != 0) else '', offset / 10)
        cursor = connection.cursor()
        print(query_ads)
        cursor.execute(query)
        non_ads = cursor.fetchall()

        cursor.execute(query_ads)

        ads = cursor.fetchall()

        list_response = []

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
        apartment_name = 16
        type_selling_id = 13
        room_detail_id = 14
        ad = 15
        type_selling_name = 17

        rooms = ads + non_ads

        if sort == "2" or sort == "3":
            rooms = sorted(rooms, key=itemgetter(4), reverse=sort == "3")

        for room in rooms:
            queryImages = RoomImages.objects.filter(room_id=room[1]).values('id', 'image', 'room')
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
                'ads': room[ad]
            })

        return JsonResponse({
            "objects": list_response
        }, content_type='application/json', status=200)

    except Exception as e:
        print(e)
        return JsonResponse({
            'error': {
                "message": str(e)
            }
        }, content_type='application/json', status=500)


def recommendation():
    try:
        order_header_set = OrderHeader.objects.filter(order_status_id__in=[1, 2]).values_list('product_id',
                                                                                              flat=True).annotate(
            product_id_count=Count('product_id')).order_by('-product_id')[:2]
        print("Order header set: {}".format(order_header_set))
        valid_ads_list = RoomAd.objects.filter(expired_date__gte=datetime.datetime.now()).values_list('room_id',
                                                                                                      flat=True)[:5]
        print("Value ads list: {}".format(valid_ads_list))

        ids = []
        if len(order_header_set) > 0:
            for data in order_header_set:
                ids.append(data)

        if len(valid_ads_list) > 0:
            for data in valid_ads_list:
                ids.append(data)
        print("List of id: {}".format(ids))
        if len(ids) < 5:
            diff = 5 - len(ids)
            print("DIFF: {}".format(diff))
            for id in Room.objects.all().exclude(product_id__in=ids).order_by('room_id').values_list('product_id',
                                                                                                     flat=True)[
                      :diff]:
                ids.append(id)
            print(ids)

        query = Room.objects.all().filter(product_id__in=ids, status=True) if len(ids) > 0 else Room.objects.filter(
            status=True).order_by('room_id')[:5]

        list_response = []
        for room in query:
            queryroomDetail = RoomDetail.objects.filter(room_id=room.room_id).values('id', 'room', 'price',
                                                                                     'type_selling')
            for roomDetail in queryroomDetail:
                typeSelling = TypeSelling.objects.filter(id=roomDetail["type_selling"]).values('id', 'name')
                typeSellingSerialized = json.dumps(list(typeSelling), cls=DjangoJSONEncoder)
                roomDetail["type_selling"] = json.loads(typeSellingSerialized)[0]

            serializedQuery = json.dumps(list(queryroomDetail), cls=DjangoJSONEncoder)
            roomDetails = json.loads(serializedQuery)

            queryImages = RoomImages.objects.filter(room_id=room.room_id).values('id', 'image', 'room')
            for image in queryImages:
                image["image"] = "/media/" + image["image"]
            serializedQuery = json.dumps(list(queryImages), cls=DjangoJSONEncoder)

            images = json.loads(serializedQuery)
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
            })
            # print(list_response)

        return JsonResponse({
            "objects": list_response
        }, content_type='application/json', status=200)

    except Exception as e:
        print(e)
        return JsonResponse({
            'error': {
                "message": str(e)
            }
        }, content_type='application/json', status=500)


class RoomResource(ModelResource):
    created_by = fields.ToOneField(UserResource, attribute='created_by', full=True, null=False)
    room_details = fields.ToManyField('api.api_resources.RoomDetailResource', 'room_detail', full=True, null=True)
    images = fields.ToManyField('api.api_resources.RoomImagesResource', 'room_images', full=True, null=True)

    class Meta:
        queryset = Room.objects.all()
        resource_name = 'room'
        allowed_methods = ['get', 'post', 'put', 'delete']
        always_return_data = True
        authorization = Authorization()  # THIS IS IMPORTANT
        filtering = {
            'room_id': ALL,
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
            # search
            url(r"^(?P<resource_name>%s)/recommendation%s$" %
                (resource_name, trailing_slash()),
                self.wrap_view('recommendation'), name="api_recommendation")
        ]

    def update(self, request):

        # function for update products
        try:
            from django.http.multipartparser import MultiPartParser
            print("RoomResource.update: masuk")
            data = self.deserialize(
                request, request.body,
                format=request.content_type
            )

            print('roomResource.update: Body {}'.format(data))

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

            print("RoomResource.update: {}".format(roomId))
            print("RoomResource.update: {}".format("prepare update"))
            Room.objects.filter(pk=roomId).update(
                name=name,
                description=description,
                contact_person_name=contactPersonName,
                contact_person_phone=contactPersonPhone,
                sqm_room=sqmRoom,
                bedroom_total=bedroomTotal,
                bathroom_total=bathroomTotal,
                guest_maximum=guestMaximum
            )

            for roomDetail in roomDetails:
                price = roomDetail.get("price", '')
                type_selling_id = roomDetail.get("type_selling_id")
                print("Loop room detail: {}".format(roomDetail))
                try:
                    pd = RoomDetail.objects.get(room_id=roomId, type_selling_id=type_selling_id)
                    pd.price = price
                    pd.save()
                    print("Update room detail: ")
                    print(roomDetail)
                except RoomDetail.DoesNotExist:
                    pd = RoomDetail.objects.create(
                        price=price,
                        type_selling_id=type_selling_id,
                        room_id=roomId
                    )
                    pd.save()
                    print("Create room detail: ")
                    print(roomDetail)
            roomDetailIds = list(map(lambda x: x.get("type_selling_id"), roomDetails))
            deletedRoomDetails = RoomDetail.objects.filter(room_id=roomId).exclude(type_selling_id__in=roomDetailIds)
            print(deletedRoomDetails)
            for roomDetail in deletedRoomDetails:
                roomDetail.delete()

            for roomImage in roomImages:
                id = roomImage.get('id', -1)
                RoomDetail.objects.filter(pk=id).delete()

            query_room_detail = RoomDetail.objects.filter(room_id=roomId).values('id', 'room', 'price', 'type_selling')
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
                'guest_maximum': guestMaximum
            }
            print(response)
            return JsonResponse(response, content_type='application/json', status=200)
        except Exception as e:
            print('roomResource.update onError: {}'.format(str(e)))
            return JsonResponse({
                'error': {
                    "message": str(e)
                }
            }, content_type='application/json', status=500)
