import json

from django.conf.urls import url
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.http import JsonResponse
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
from api.models.apartment.apartment import Apartment
from api.models.apartment.tower import Tower


class ApartmentResource(ModelResource):
    towers = fields.ToManyField('api.api_resources.aparment.tower_resource.TowerResource', full=True,
                                null=True,
                                attribute=lambda bundle: Tower.objects.filter(
                                    active=True,
                                    apartment=bundle.obj
                                ))

    # room_details = fields.ToManyField(RoomDetailResource, 'room_detail', full=True, null=True)
    class Meta:
        queryset = Apartment.objects.filter(active=True)
        resource_name = 'apartment'
        always_return_data = True
        list_allowed_methods = ['get', 'post', 'put']
        authorization = Authorization()
        filtering = {
            'id': ALL
        }

    def prepend_urls(self):
        """ Add the following array of urls to the UserResource base urls """
        resource_name = self._meta.resource_name
        return [
            # update
            url(r"^(?P<resource_name>%s)/create_apartment%s$" %
                (resource_name, trailing_slash()),
                self.wrap_view('create_apartment'), name="api_create_apartment")
        ]

    def create_apartment(self, request, **kwargs):
        # function for create/update apartment
        try:
            from django.http.multipartparser import MultiPartParser
            with transaction.atomic():
                data = self.deserialize(
                    request, request.body,
                    format=request.content_type
                )

                id = data.get('id', 0)
                name = data.get('name', '')
                towers = data.get('towers', [])

                try:
                    pd = Apartment.objects.get(id=id)
                    pd.name = name
                    pd.save()
                except Apartment.DoesNotExist:
                    pd = Apartment.objects.create(
                        name=name
                    )
                    pd.save()

                for tower in towers:
                    name_tower = tower.get("name", '')
                    active_tower = tower.get("active", True)
                    id_tower = tower.get("id", 0)
                    try:
                        td = Tower.objects.get(id=id_tower)
                        td.apartment = pd
                        td.name = name_tower
                        td.active = active_tower
                        td.save()
                    except Tower.DoesNotExist:
                        td = Tower.objects.create(
                            name=name_tower,
                            apartment=pd
                        )
                        td.save()

                query_tower = Tower.objects.filter(apartment__id=pd.id, active=True).values('id',
                                                                                            'name')

                serializedQuery = json.dumps(list(query_tower), cls=DjangoJSONEncoder)
                towers = json.loads(serializedQuery)
                response = {
                    'id': id,
                    'name': name,
                    'towers': towers
                }
                return JsonResponse(response, content_type='application/json', status=200)
        except Exception as e:
            return JsonResponse({
                'error': {
                    "message": str(e)
                }
            }, content_type='application/json', status=500)
