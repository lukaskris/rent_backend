import json
import logging

from django.conf.urls import url
from django.http import JsonResponse
from fcm_django.models import FCMDevice
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource

logger = logging.getLogger('api.fcm')


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
                resource_name,
                self.wrap_view('register'), name="api_fcm_register"),
        ]

    def register(self, request, **kwargs):
        logger.info('FCMDeviceResource.register')
        data = self.deserialize(
            request, request.body,
            format=request.content_type
        )
        deviceId = data['device_id']
        registrationId = data['registration_id']
        userId = data['user_id']
        name = data['name']
        data_type = data['type']
        logger.info('FCMDeviceResource.register: {}'.format(json.dumps(data)))
        try:
            device = FCMDevice.objects.get(device_id=deviceId)
            logger.info(device)
            device.registration_id = registrationId
            device.user_id = userId
            device.type = data_type
            device.name = name
            device.save()
            return JsonResponse({
                'message': 'success'
            }, content_type='application/json', status=200)
        except FCMDevice.DoesNotExist:
            FCMDevice.objects.create(
                device_id=deviceId,
                registration_id=registrationId,
                user_id=userId,
                type=data_type,
                active=True,
                name=name
            )
            return JsonResponse({
                'message': 'success'
            }, content_type='application/json', status=200)
        except Exception as e:
            logger.exception(e)
            return JsonResponse({
                'message': str(e)
            }, content_type='application/json', status=500)
