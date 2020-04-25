from api.decorators import api_method
from api.decorators import required_fields
import requests
from tastypie import fields
from tastypie import http
from tastypie.http import HttpUnauthorized, HttpForbidden
from tastypie.authorization import Authorization
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.exceptions import Unauthorized
from tastypie.utils import trailing_slash
from tastypie.models import ApiKey
from tastypie.authentication import Authentication, ApiKeyAuthentication
from tastypie.resources import ModelResource
from tastypie.paginator import Paginator
from django.db.models import signals, Sum
from tastypie.models import create_api_key
from api.models import OrderStatus, User, Room, Product, Feature, Notification, RoomAd, AdsBundle, AdsOrder, OrderHeader, TypeSelling, OrderDetail, RoomImages, RoomDetail
from django.contrib.auth.hashers import make_password
from django.conf.urls import url
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.conf import settings
from django.http import HttpResponse
from datetime import datetime as dtime, timedelta
from tastypie.constants import ALL
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from fcm_django.models import FCMDevice

import datetime

# models
from api.models import User

import json, logging, jwt

# Get an instance of a logger
logger = logging.getLogger('api.user')

class MultipartResource(object):

    def deserialize(self, request, data, format=None):
        if not format:
            format = request.META.get('CONTENT_TYPE', 'application/json')
        if format == 'application/x-www-form-urlencoded':
            return request.POST

        if format.startswith('multipart/form-data'):
            multipart_data = request.POST.copy()
            multipart_data.update(request.FILES)
            return multipart_data

        return super(MultipartResource, self).deserialize(request, data, format)

    def put_detail(self, request, **kwargs):
        if request.META.get('CONTENT_TYPE', '').startswith('multipart/form-data') and not hasattr(request, '_body'):
            request._body = ''
        return super(MultipartResource, self).put_detail(request, **kwargs)

    def patch_detail(self, request, **kwargs):
        if request.META.get('CONTENT_TYPE', '').startswith('multipart/form-data') and not hasattr(request, '_body'):
            request._body = ''
        return super(MultipartResource, self).patch_detail(request, **kwargs)

class UserResource(ModelResource):
    """Get and update user profile."""

    class Meta:
        """ Metadata for the user resource """
        queryset = User.objects.all()
        resource_name = 'users'
        allowed_methods = ['get', 'post']
        always_return_data = True
        excludes = ('password', 'is_superuser', 'is_active', 'date_joined')

    def prepend_urls(self):
        """ Add the following array of urls to the UserResource base urls """
        resource_name = self._meta.resource_name
        return [
            # register
            url(r"^(?P<resource_name>%s)/register%s$" %
                (resource_name, trailing_slash()),
                self.wrap_view('register'), name="api_register"),
            # login
            url(r"^(?P<resource_name>%s)/login%s$" %
                (resource_name, trailing_slash()),
                self.wrap_view('login'), name="api_login"),
            # logout
            url(r'^(?P<resource_name>%s)/logout%s$' %
                (resource_name, trailing_slash()),
                self.wrap_view('logout'), name='api_logout'),
            # is_authenticated
            url(r'^(?P<resource_name>%s)/is_authenticated%s$' %
                (resource_name, trailing_slash()),
                self.wrap_view('authenticated'), name='api_authenticated'),
            # recover password
            url(r'^(?P<resource_name>%s)/recover_password%s$' %
                (resource_name, trailing_slash()),
                self.wrap_view('recover_password'),
                name='api_recover_password'),
        ]

    def authenticated(self, request, **kwargs):
        """ api method to check whether a user is authenticated or not"""

        self.method_check(request, allowed=['get'])
        user = request.user
        if user.is_authenticated():

            bundle = self.build_bundle(obj=user, request=request)
            bundle = self.full_dehydrate(bundle)
            bundle = self.alter_detail_data_to_serialize(request, bundle)

            return self.create_response(request, bundle)
        else:
            return self.create_response(request, False)

    def recover_password(self, request, **kwargs):
        """ Sets a token to recover the password and sends an email with
        the token

        """
        self.method_check(request, allowed=['post'])

        data = self.deserialize(
            request, request.body,
            format=request.META.get('CONTENT_TYPE', 'application/json')
        )
        email = data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            response = http.HttpBadRequest(
                json.dumps("User with email %s not found" % email),
                content_type=request.META['CONTENT_TYPE'])
            raise ImmediateHttpResponse(response=response)

        user.send_recover_password_email(request)

        return self.create_response(request, {'success': True})

    def login(self, request, **kwargs):
        """ A new end point for login the user using the django login system

        """
        try:
            data = self.deserialize(
                request, request.body,
                format=request.content_type
            )

            print('UserResource.login: {}'.format(json.dumps(data)))

            email = data.get('email', '')
            password = data.get('password', '')
            print(email, password)
            user = authenticate(username=email, password=password)
            if user:
                print('UserResource.login: user found')
                if user.is_active:
                    login(request, user)
                    print('UserResource.login: login successful')
                    try:
                        userData = User.objects.get(email=email)
                        return JsonResponse({
                            'meta': {
                                'message': ''
                            },
                            'objects': [
                                {
                                    'id': userData.id,
                                    'email': email,
                                    'password': password,
                                    'name': userData.name,
                                    'is_staff': int(userData.is_staff == True),
                                    'phone_number': str(userData.phone_number),
                                    'image_url': str(userData.image_url)
                                }
                            ],
                            'error': {}
                        }, content_type='application/json', status=200)
                    except Exception as e:
                        print(e)
                else:
                    print('UserResource.login: login fail, user not active')
                    return JsonResponse({
                        'meta': {},
                        'objects': [],
                        'error': {
                            'message': 'User not active'
                        }
                    }, content_type='application/json', status=403)
            else:
                print("UserResource.login: Login fail, username or password incorrect")
                return JsonResponse({
                    'meta': {},
                    'objects': [],
                    'error': {
                        'message': 'Username or password incorrect'
                    }
                }, content_type='application/json', status=401)
        except:
            return JsonResponse({
                'meta': {},
                'objects': [],
                'error': {
                    'message': 'Internal server error'
                }
            }, content_type='application/json', status=500)

    def logout(self, request, **kwargs):
        """
        A new end point to logout the user using the django login system
        """
        self.method_check(request, allowed=['delete'])
        if request.user and request.user.is_authenticated():
            logout(request)

        return self.create_response(request, {'success': True})

    def register(self, request, **kwargs):
        logger.debug('UserResource.register')
        data = self.deserialize(
            request, request.body,
            format=request.content_type
        )

        print('UserResource.register: {}'.format(json.dumps(data)))

        email = data.get('email', '')
        password = data.get('password', '')

        # try to geet the user by email
        try:
            user = User.objects.get(email=email)
            print(user)
            return JsonResponse({
                'objects': [],
                'error': {
                    "message": "This email is already registered"
                }
            }, content_type='application/json', status=400)
        except User.DoesNotExist:
            # the user with this email does not exist
            try:
                user = User.objects.get(phone_number=data['phone_number'])

                return JsonResponse({
                    'objects': [],
                    'error': {
                        "message": "This phone is already registered"
                    }
                }, content_type='application/json', status=400)
            except User.DoesNotExist:
                # create a new user
                user = User.objects.create(
                    email=email,
                    name=data.get('name', ''),
                    phone_number=data['phone_number'],
                    is_staff=data['is_staff'])
                user.set_password(data['password'])
                user.save()
                user = authenticate(email=email, password=data['password'])
                login(request, user)
                print('UserResource.Register: login successful')
                return JsonResponse({
                    'meta': {
                        'message': ''
                    },
                    'objects': [
                        {
                            'id': user.id,
                            'email': email,
                            'password': password,
                            'name': user.name,
                            'is_staff': int(user.is_staff == True),
                            'phone_number': str(user.phone_number),
                            'image_url': str(user.image_url)
                        }
                    ],
                    'error': {}
                }, content_type='application/json', status=200)

class RoomResource(ModelResource):
    created_by = fields.ToOneField(UserResource, attribute='created_by', full=True, null=False)
    room_details = fields.ToManyField('api.resources.RoomDetailResource', 'room_detail', full=True, null=True)
    images = fields.ToManyField('api.resources.RoomImagesResource', 'room_images', full=True, null=True)
    class Meta:
        queryset = Room.objects.all()
        resource_name = 'room'
        allowed_methods = ['get', 'post', 'put', 'delete']
        always_return_data = True
        authorization = Authorization() # THIS IS IMPORTANT


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
                self.wrap_view('search'), name="api_search")
        ]

    def update(self, request, **kwargs):

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
                sqm_room = sqmRoom,
                bedroom_total = bedroomTotal,
                bathroom_total = bathroomTotal,
                guest_maximum = guestMaximum
            )

            for roomDetail in roomDetails:
                id = roomDetail.get("id")
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
                        type_selling_id = type_selling_id,
                        room_id=roomId
                    )
                    pd.save()
                    print("Create room detail: ")
                    print(roomDetail)
            roomDetailIds = list(map(lambda x : x.get("type_selling_id"), roomDetails))
            deletedRoomDetails = RoomDetail.objects.filter(room_id=roomId).exclude(type_selling_id__in = roomDetailIds)
            print(deletedRoomDetails)
            for roomDetail in deletedRoomDetails:
                roomDetail.delete()

            for roomImage in roomImages:
                id = roomImage.get('id', -1)
                RoomDetail.objects.filter(pk=id).delete()

            queryroomDetail = RoomDetail.objects.filter(room_id=roomId).values('id', 'room', 'price', 'type_selling')
            for roomDetail in queryroomDetail:
                typeSelling = TypeSelling.objects.filter(id=roomDetail["type_selling"]).values('id', 'name')
                typeSellingSerialized = json.dumps(list(typeSelling), cls= DjangoJSONEncoder)
                roomDetail["type_selling"] = json.loads(typeSellingSerialized)[0]

            serializedQuery = json.dumps(list(queryroomDetail), cls=DjangoJSONEncoder)
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

    def search(self, request, **kwargs):
        try:
            check_in_time = dtime.strptime(request.GET.get('check_in'), '%d%m%Y')
            check_out_time = dtime.strptime(request.GET.get('check_out'), '%d%m%Y')
            order_header_set = OrderHeader.objects.values_list('product_id', flat=True).filter(check_in_time=check_in_time, check_out_time=check_out_time)
            print(order_header_set)
            query = Room.objects.all().exclude(product_id__in=order_header_set)
            list_response = []
            for room in query:
                queryroomDetail = RoomDetail.objects.filter(room_id=room.room_id).values('id', 'room', 'price', 'type_selling')
                for roomDetail in queryroomDetail:
                    typeSelling = TypeSelling.objects.filter(id=roomDetail["type_selling"]).values('id', 'name')
                    typeSellingSerialized = json.dumps(list(typeSelling), cls= DjangoJSONEncoder)
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
                print(list_response)
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


class RoomDetailResource(ModelResource):
    room = fields.ToOneField(RoomResource, 'room')
    type_selling = fields.ToOneField('api.resources.TypeSellingResource', 'type_selling', full=True, null=False)
    class Meta:
        queryset = RoomDetail.objects.all()
        resource_name = 'room_detail'
        allowed_methods = ['get', 'post', 'put', 'delete']
        authorization = Authorization()
        always_return_data = True

class RoomImagesResource(MultipartResource, ModelResource):
    room = fields.ToOneField('api.resources.RoomResource', 'room')
    class Meta:
        queryset = RoomImages.objects.all()
        resource_name = 'room_images'
        allowed_methods = ['get', 'post', 'delete']
        authorization = Authorization()
        always_return_data = True

class TypeSellingResource(ModelResource):
    room_detail = fields.ToManyField('api.resources.RoomDetailResource', 'room_detail_set', related_name='type_selling', null=True)
    class Meta:
        queryset = TypeSelling.objects.all()
        resource_name = 'type_selling'
        authorization = Authorization()

class SearchResource(ModelResource):
    created_by = fields.ToOneField(UserResource, attribute='created_by', full=True, null=False)
    product_details = fields.ToManyField('api.resources.ProductDetailResource', 'product_detail', full=True, null=True)
    images = fields.ToManyField('api.resources.ProductImagesResource', 'product_images', full=True, null=True)
    class Meta:
        queryset = Room.objects.all()
        resource_name = 'search'
        allowed_methods = ['get']
        always_return_data = True

class FeaturesResource(ModelResource):
    class Meta:
        queryset = Feature.objects.all()
        resource_name = 'features'

class RoomAdResource(ModelResource):
    room = fields.ToOneField(RoomResource, 'room')
    class Meta:
        queryset = RoomAd.objects.all()
        resource_name = 'room_ad'
        object_class = RoomAd
        allowed_methods = ['get', 'post']
        authorization = Authorization() # THIS IS IMPORTANT


    def prepend_urls(self):
        """ Add the following array of urls to the UserResource base urls """
        resource_name = self._meta.resource_name
        return [
            # update
            url(r"^(?P<resource_name>%s)/get_count%s$" %
                (resource_name, trailing_slash()),
                self.wrap_view('get_count'), name="api_get_count")
        ]

    def get_count(self, request, **kwargs):
        room = RoomAd.objects.all().filter(room_id=request.GET.get('room_id'),active=True, expired_date__gte=datetime.date.today()).aggregate(Sum('click'))
        print('roomResource.update: room {}'.format(room))
        return JsonResponse({
            'click': room["click__sum"]
        }, content_type='application/json', status=200)

class AdsBundleResource(ModelResource):
    created_by = fields.ToOneField(UserResource, attribute='created_by', full=True, null=False)
    class Meta:
        queryset = AdsBundle.objects.all()
        allowed_methods = ['get', 'post', 'put', 'delete']
        authorization = Authorization() # THIS IS IMPORTANT
        resource_name = 'ads_bundle'
        always_return_data = True

class ProductResource(ModelResource):
    created_by = fields.ToOneField(UserResource, attribute='created_by', full=True, null=False)
    class Meta:
        queryset = Product.objects.all()
        allowed_methods = ['get']
        authorization = Authorization() # THIS IS IMPORTANT
        resource_name = 'product'
        always_return_data = True

class AdsOrderResource(ModelResource):
    class Meta:
        queryset = AdsOrder.objects.all()
        resource_name = 'ads_order'

class OrderStatusResource(ModelResource):
    class Meta:
        queryset = OrderStatus.objects.all()
        resource_name = 'order_status'

class OrderHeaderResource(ModelResource):
    type_selling = fields.ToOneField(TypeSellingResource, attribute='type_selling', full=True, null=True)
    order_status = fields.ToOneField(OrderStatusResource, attribute='order_status', full=True, null=True)
    product = fields.ToOneField(ProductResource, attribute='product', full=True, null=True)

    class Meta:
        queryset = OrderHeader.objects.all()
        resource_name = 'order'
        filtering = {
            'user_id': ALL
        }

    def prepend_urls(self):
        """ Add the following array of urls to the UserResource base urls """
        resource_name = self._meta.resource_name
        return [
            # charge
            url(r"^(?P<resource_name>%s)/charge$" %
                (resource_name),
                self.wrap_view('charge'), name="api_charge"),
        ]

    def charge(self, request, **kwargs):
        try:
            logger.debug('OrderHeaderResource.payment')
            data = self.deserialize(
                request, request.body,
                format=request.content_type
            )

            print('OrderHeaderResource.payment: {}'.format(json.dumps(data)))

            import base64

            auth = settings.MIDTRANS_SERVER_KEY_SANDBOX
            base64_bytes = base64.b64encode(auth.encode('ascii'))
            base64_auth = base64_bytes.decode('ascii')

            headers = {
              'Authorization': 'Basic ' + base64_auth,
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            }

            DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
            customField2 = data['custom_field2'].split('|')
            checkIn = customField2[0]
            checkOut = customField2[1]

            if("custom_field1" in data):
                order_header = OrderHeader.objects.create(
                    midtrans_id = data["transaction_details"]["order_id"],
                    product_id = data['item_details'][0]['id'],
                    type_selling_id = data['custom_field1'],
                    grand_total = data['transaction_details']['gross_amount'],
                    user_id = data['custom_field3'],
                    payment_date = datetime.date.today(),
                    order_status_id = 1,
                    expired_date = datetime.date.today() + timedelta(days=1),
                    check_in_time = datetime.datetime.strptime(checkIn, DATETIME_FORMAT),
                    check_out_time = datetime.datetime.strptime(checkOut, DATETIME_FORMAT)
                )
                order_header.save()
                response = requests.request("POST", settings.MIDTRANS_SANDBOX, headers=headers, data = json.dumps(data))
                print(response.json())
                return HttpResponse(
                    content=response.content,
                    status=response.status_code,
                    content_type=response.headers['Content-Type']
                )
            else:
                order_header = OrderHeader.objects.create(
                    midtrans_id = data["transaction_details"]["order_id"],
                    product_id = data['item_details'][0]['id'],
                    type_selling_id = None,
                    grand_total = data['transaction_details']['gross_amount'],
                    user_id = data['custom_field3'],
                    payment_date = datetime.date.today(),
                    order_status_id = 1,
                    expired_date = datetime.date.today() + timedelta(days=1),
                    check_in_time = datetime.date.today(),
                    check_out_time = datetime.date.today()
                )
                order_header.save()
                response = requests.request("POST", settings.MIDTRANS_SANDBOX, headers=headers, data = json.dumps(data))
                print(response.json())
                return HttpResponse(
                    content=response.content,
                    status=response.status_code,
                    content_type=response.headers['Content-Type']
                )


        except Exception as e:
            print("Exception: {}".format(e));
            return HttpResponse(
                content={
                    'error': {
                        "message": e
                    }
                },
                status=500,
                content_type="application/json"
            )

class OrderDetailResource(ModelResource):
    class Meta:
        queryset = OrderDetail.objects.all()
        resource_name = 'order_detail'
        authentication = ApiKeyAuthentication()

class FCMDeviceResource(ModelResource):
    class Meta:
        queryset = FCMDevice.objects.all()
        resource_name = 'devices'
        authorization = Authorization()


    def prepend_urls(self):
        """ Add the following array of urls to the UserResource base urls """
        resource_name = self._meta.resource_name
        return [
            # charge
            url(r"^(?P<resource_name>%s)/register/$" %
                (resource_name),
                self.wrap_view('register'), name="api_rregister"),
        ]


    def register(self, request, **kwargs):
        logger.debug('FCMDeviceResource.register')
        data = self.deserialize(
            request, request.body,
            format=request.content_type
        )
        deviceId = data['device_id']
        registrationId = data['registration_id']
        userId = data['user_id']
        name = data['name']
        type = data['type']
        print('FCMDeviceResource.register: {}'.format(json.dumps(data)))
        try:
            device = FCMDevice.objects.get(device_id=deviceId)
            print(device)
            device.registration_id = registrationId
            device.user_id = userId
            device.type = type
            device.name = name
            device.save()
            return JsonResponse({
                'message': 'success'
            }, content_type='application/json', status=200)
        except FCMDevice.DoesNotExist:
            FCMDevice.objects.create(
                device_id = deviceId,
                registration_id = registrationId,
                user_id = userId,
                type = type,
                active = True,
                name = name
            )
            return JsonResponse({
                'message': 'success'
            }, content_type='application/json', status=200)
        except Exception as e:
            print(e)
            return JsonResponse({
                'message': str(e)
            }, content_type='application/json', status=500)

class NotificationResource(ModelResource):
    class Meta:
        queryset = Notification.objects.all()
        resource_name = 'notification'
        authorization = Authorization()

    def prepend_urls(self):
        """ Add the following array of urls to the UserResource base urls """
        resource_name = self._meta.resource_name
        return [
            # update
            url(r"^(?P<resource_name>%s)/handling/$" %
                (resource_name),
                self.wrap_view('handling'), name="api_handling")
        ]

    def handling(self, request, **kwargs):
        try:
            print("NotificationResource.handling: masuk")
            data = self.deserialize(
                request, request.body,
                format=request.content_type
            )

            print('NotificationResource.handling: Body {}'.format(data))

            midtrans_id = data.get("order_id", "")
            payment_type = data.get("payment_type", "")
            transaction_status = data.get("transaction_status", "")

            payment_number = ""
            transaction_type = ""
            order_status_id = 1
            message_notification = ""

            if payment_type == "bank_transfer" and "permata_va_number" in data.keys():
                #permata bank
                transaction_type = "permata"
                payment_number = data.get("permata_va_number", '')
            elif payment_type == "bank_transfer" and "va_numbers" in data.keys():
                va = data.get('va_numbers')
                payment_number = va[0].get('va_number', '')
                transaction_type = va[0].get('bank', '')
            elif payment_type == "bank_transfer" and "bill_key" in data.keys():
                bill_key = data.get('bill_key', '')
                biller_code = data.get('biller_code', '')
                payment_number = bill_key
                transaction_type = 'mandiri'
            elif payment_type == "bca_klikpay" or payment_type == 'bca_klikbca':
                transaction_type = payment_type
                if "approval_code" in data.keys():
                    payment_number = data.get('approval_code', '')
            elif payment_type == "cstore":
                transaction_type = data.get('store', '')
                payment_number = data.get('payment_code', '')

            if transaction_status == "pending":
                message_notification = "Transaksi sedang menunggu pembayaran!."
                order_status_id = 1
            elif transaction_status == "settlement":
                message_notification = "Pembayaran berhasil di verifikasi"
                order_status_id = 2
            elif transaction_status == "expire" or transaction_status == "cancel":
                message_notification = "Pembayaran telah lewat waktu yang ditentukan"
                order_status_id = 3

            order_header = OrderHeader.objects.get(midtrans_id=midtrans_id)
            order_header.payment_number = payment_number
            order_header.payment_type = transaction_type
            order_header.order_status_id = order_status_id
            order_header.save()
            print("Order header saved {}".format(order_header))

            Notification.objects.create(
                user_id = order_header.user_id,
                message = message_notification,
                order_header_id = order_header.id
            )
            print("Notification saved")
            device = FCMDevice.objects.get(user_id=order_header.user_id)

            print("Device get {}".format(device))
            print("Order header type selling {}".format(order_header.type_selling_id))
            message_data = {
                "order_header_id": str(order_header.id),
                "type": "Ad" if order_header.type_selling_id == None else "Room"
            }
            print("Message data {}".format(message_data))
            device.send_message(title="Pembayaran", body=message_notification, data=message_data)
            return JsonResponse({
                'success': {
                    "message": "true"
                }
            }, content_type='application/json', status=200)
        except Exception as e:
            print('roomResource.update onError: {}'.format(str(e)))
            return JsonResponse({
                'error': {
                    "message": str(e)
                }
            }, content_type='application/json', status=500)
