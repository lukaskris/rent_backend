# Get an instance of a logger
import json
import logging

from django.conf.urls import url
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from tastypie import http, fields
from tastypie.authorization import Authorization
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash

from api.api_resources.helper.multipart_request import MultipartResource
from api.models.user.user import User

logger = logging.getLogger('api.user')


class UserResource(MultipartResource, ModelResource):
    class Meta:
        """ Metadata for the user resource """
        queryset = User.objects.all()
        resource_name = 'users'
        allowed_methods = ['get', 'post', 'put']
        always_return_data = True
        excludes = ('password', 'is_superuser', 'is_active', 'date_joined')
        authorization = Authorization()

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

    def logout(self, request):
        """
        A new end point to logout the user using the django login system
        """
        self.method_check(request, allowed=['delete'])
        if request.user and request.user.is_authenticated():
            logout(request)

        return self.create_response(request, {'success': True})

    def register(self, request, **kwargs):
        logger.info('UserResource.register')
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
                User.objects.get(phone_number=data['phone_number'])
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
