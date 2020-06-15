"""rent_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from tastypie.api import Api

from api.api_resources.ads.ads_bundle_resource import AdsBundleResource
from api.api_resources.ads.room_ad_resource import RoomAdResource
from api.api_resources.aparment.apartment_resource import ApartmentResource
from api.api_resources.balance.balance_history_resource import BalanceHistoryResource
from api.api_resources.balance.balance_user_resource import BalanceUserResource
from api.api_resources.banner.banner_resource import BannerResource
from api.api_resources.commission.commission_resource import CommissionResource
from api.api_resources.fcm_resource import FCMDeviceResource
from api.api_resources.notification_resource import NotificationResource
from api.api_resources.order.order_detail_resource import OrderDetailResource
from api.api_resources.order.order_header import OrderHeaderResource
from api.api_resources.order.order_status_resource import OrderStatusResource
from api.api_resources.order.type_selling import TypeSellingResource
from api.api_resources.product.product_resource import ProductResource
from api.api_resources.room.feature_resource import FeaturesResource
from api.api_resources.room.room_detail_resource import RoomDetailResource
from api.api_resources.room.room_images_resource import RoomImagesResource
from api.api_resources.room.room_resource import RoomResource
from api.api_resources.user_resource import UserResource

v1_api = Api(api_name='v1')
v1_api.register(OrderStatusResource())
v1_api.register(ApartmentResource())
v1_api.register(FCMDeviceResource())
v1_api.register(UserResource())
v1_api.register(OrderDetailResource())
v1_api.register(OrderHeaderResource())
v1_api.register(ProductResource())
v1_api.register(NotificationResource())
v1_api.register(RoomAdResource())
v1_api.register(FeaturesResource())
v1_api.register(RoomResource())
v1_api.register(RoomDetailResource())
v1_api.register(TypeSellingResource())
v1_api.register(RoomImagesResource())
v1_api.register(BannerResource())
v1_api.register(AdsBundleResource())
v1_api.register(BalanceHistoryResource())
v1_api.register(BalanceUserResource())
v1_api.register(CommissionResource())

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(v1_api.urls))
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
