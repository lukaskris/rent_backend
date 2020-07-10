from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL
from tastypie.resources import ModelResource

from api.models.room.product import Product
from api.api_resources.user_resource import UserResource


class ProductResource(ModelResource):
    created_by = fields.ToOneField(UserResource, attribute='created_by', full=True, null=True)

    class Meta:
        queryset = Product.objects.all()
        allowed_methods = ['get']
        authorization = Authorization()  # THIS IS IMPORTANT
        resource_name = 'product'
        always_return_data = True
        filtering = {
            'product_id': ALL
        }
