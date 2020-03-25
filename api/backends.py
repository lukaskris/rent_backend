from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from api.models import User

class CustomBackend(BaseBackend):
    """docstring for CustomBackend."""
    def authenticate(self, request, username=None, password=None):
        #check username and password and return a user
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
