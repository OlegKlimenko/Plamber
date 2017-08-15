# -*- coding: utf-8 -*-

import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from rest_framework.decorators import api_view
from rest_framework.response import Response

from app.models import TheUser
from app.tasks import restore_account
from app.utils import generate_password

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def user_login(request):
    """
    Authenticates user and returns the token which uses to access to the API.
    """
    user = authenticate(username=request.data.get('username'),
                        password=request.data.get('password'))
    if user:
        user_token = TheUser.objects.get(id_user=user).auth_token

        login(request, user)
        logger.info("User '{}' logged in.".format(user.username))

        return Response({'status': 200,
                         'detail': 'successful',
                         'data': {'token': user_token}})

    return Response({'status': 404,
                     'detail': 'not authenticated',
                     'data': {'token': None}})


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def restore_data(request):
    """
    Sends mail to restore user data.
    """
    with transaction.atomic():
        temp_password = generate_password()

        try:
            user = User.objects.get(email=request.data.get('email'))
            user.set_password(temp_password)
            user.save()

            restore_account.delay(user.username, temp_password, request.data.get('email'))

            logger.info("The password for user: '{}' restored successfully.".format(user))

            return Response({'status': 200,
                             'detail': 'successful',
                             'data': {}})

        except ObjectDoesNotExist:
            return Response({'status': 404,
                             'detail': 'not exists',
                             'data': {}})
