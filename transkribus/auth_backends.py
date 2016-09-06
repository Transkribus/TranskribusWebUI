import logging

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


from . import services
from . import helpers

from .models import UserInfo, User


logger = logging.getLogger('transkribus.auth_backends')

# Provides authentication backend for Transkribus REST API. This is
# a refactored version of the backend implementation created for
# TranskribusWebUI: https://github.com/Transkribus/TranskribusWebUI
# Creates user if it does not already exists. Updates fields for
# exising users. Also, associates and updates extra information.

class TranskribusBackend(ModelBackend):
    """
    Transkribus authentication backend.

    """

    def authenticate(self, username=None, password=None):

        # XXX Is this really needed??
        if not username or not password:
            # logger.debug("Discarding invalid username or password for user %s", username)
            return None

        user_data = services.login(username, password)

        if not user_data:
            # logger.debug("Login failed for user %r", username)
            return None

        try:
            user = User.objects.get(username=user_data['username'])

        except User.DoesNotExist:
            user = User.create(**user_data)
            UserInfo.create(user=user, **user_data)
            # logger.debug("Created new user %s with pk %s", user.username, user.pk)
            return user

        else:
            user.update(**user_data)

        user_info, created = UserInfo.objects.get_or_create(user_id=user.pk)
        user_info.update(**user_data)

        # logger.info("Login from %s as %s", user_data.get('ip'), user_data['username'])

        return user
