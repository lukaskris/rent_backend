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
from django.conf.urls import url, include
from django.contrib import admin
from tastypie.api import Api
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from api_v2 import views
from api.resources import SearchResource, ProductDetailsResource, AdsBundleResource, OrderStatusResource, TypeSellingResource, UserResource, ProductsResource, ProductImagesResource, OrderDetailResource, OrderHeaderResource, AdsOrderResource, AdsResource, FeaturesResource

v1_api = Api(api_name='v1')
v1_api.register(OrderStatusResource())
v1_api.register(UserResource())
v1_api.register(OrderDetailResource())
v1_api.register(OrderHeaderResource())
v1_api.register(AdsOrderResource())
v1_api.register(AdsResource())
v1_api.register(FeaturesResource())
v1_api.register(ProductsResource())
v1_api.register(ProductDetailsResource())
v1_api.register(TypeSellingResource())
v1_api.register(SearchResource())
v1_api.register(ProductImagesResource())
v1_api.register(AdsBundleResource())

v2_api = routers.DefaultRouter()
v2_api.register(r'users', views.UserViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(v1_api.urls)),
    url(r'^api_v2/', include('rest_framework.urls', namespace='rest_framework'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
