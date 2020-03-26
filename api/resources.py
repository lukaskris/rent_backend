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
from django.db.models import signals
from tastypie.models import create_api_key
from api.models import OrderStatus, User, Products, Features, Ads, AdsOrder, OrderHeader, TypeSelling, OrderDetail, ProductImages, ProductsDetail
from django.contrib.auth.hashers import make_password
from django.conf.urls import url
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.conf import settings
from django.http import HttpResponse
from datetime import datetime, timedelta
from tastypie.constants import ALL

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
            # create a new user
            user = User.objects.create(
                email=email,
                name=data.get('name', ''),
                phone_number=data['phone_number'],
                is_staff=data['is_staff'])
            user.set_password(data['password'])
            user.save()

        user = authenticate(email=email, password=data['password'])

        try:
            login(bundle.request, user)
            return JsonResponse({
                'meta': {},
                'objects': [],
                'error': {}
            }, content_type='application/json', status=200)
        except:
            return JsonResponse({
                'objects': [],
                'error': {
                    "message": "This email is already registered"
                }
            }, content_type='application/json', status=200)

class ProductImagesResource(MultipartResource, ModelResource):
    product_id = fields.IntegerField(attribute='product_id', null=False)
    class Meta:
        queryset = ProductImages.objects.all()
        resource_name = 'product_images'
        authorization = Authorization()
        always_return_data = True

class ProductDetailsResource(ModelResource):
    class Meta:
        queryset = ProductsDetail.objects.all()
        resource_name = 'product_details'

class TypeSellingResource(ModelResource):
    class Meta:
        queryset = TypeSelling.objects.all()
        resource_name = 'type_selling'

class ProductsResource(ModelResource):
    created_by_id = fields.IntegerField(attribute='created_by_id', null=False)
    product_images = fields.ToManyField(ProductImagesResource, 'product', full=True, null=True)
    product_details = fields.ToManyField(ProductDetailsResource, 'product_detail', full=True, null=True)
    class Meta:
        queryset = Products.objects.all()
        resource_name = 'products'
        paginator_class = Paginator
        allowed_methods = ['get', 'post']
        always_return_data = True


class FeaturesResource(ModelResource):
    class Meta:
        queryset = Features.objects.all()
        resource_name = 'features'
        authentication = ApiKeyAuthentication()

class AdsResource(ModelResource):
    class Meta:
        queryset = Ads.objects.all()
        resource_name = 'ads'
        authentication = ApiKeyAuthentication()

class AdsOrderResource(ModelResource):
    class Meta:
        queryset = AdsOrder.objects.all()
        resource_name = 'ads_order'
        authentication = ApiKeyAuthentication()

class OrderStatusResource(ModelResource):
    class Meta:
        queryset = OrderStatus.objects.all()
        resource_name = 'order_status'


class OrderHeaderResource(ModelResource):
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

            order_header = OrderHeader.objects.create(
                midtrans_id = data["transaction_details"]["order_id"],
                product_id = data['item_details'][0]['id'],
                type_selling_id = data['custom_field1'],
                invoice_ref_number = "INV/10.102039/10102020",
                grand_total = data['transaction_details']['gross_amount'],
                user_id = data['custom_field3'],
                payment_date = datetime.now(),
                order_status_id = 1,
                expired_date = datetime.now() + timedelta(days=1),
                check_in_time = datetime.strptime(checkIn, DATETIME_FORMAT),
                check_out_time = datetime.strptime(checkOut, DATETIME_FORMAT)
            )
            order_header.save()

            # OrderDetail.objects.create(
            #     order_header = order_header,
            #     feature =
            # )

            response = requests.request("POST", settings.MIDTRANS_SANDBOX, headers=headers, data = json.dumps(data))
            print(response.json())


            return HttpResponse(
                content=response.content,
                status=response.status_code,
                content_type=response.headers['Content-Type']
            )
        except Exception as e:
            print(e);
            return HttpResponse(
                content={
                    'error': {
                        "message": "Internal server error"
                    }
                },
                status=404,
                content_type="application/json"
            )

class OrderDetailResource(ModelResource):
    class Meta:
        queryset = OrderDetail.objects.all()
        resource_name = 'order_detail'
        authentication = ApiKeyAuthentication()
