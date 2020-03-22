from tastypie.http import HttpUnauthorized
from tastypie.authentication import Authentication
from django.core.exceptions import ObjectDoesNotExist

class TokenAuthentication(Authentication):

    def is_authenticate(self, request):
        auth = request.
