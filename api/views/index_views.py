# -*- coding: utf-8 -*-

import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from rest_framework.decorators import api_view
from rest_framework.response import Response

from app.models import TheUser
from app.tasks import restore_account, successful_registration
from app.utils import generate_password
from ..utils import invalid_data_response
from ..serializers.request_serializers import (UserLoginRequest,
                                               RestoreDataRequest,
                                               UserExistsRequest,
                                               EmailExistsRequest,
                                               SignInRequest)

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def user_login(request):
    """
    Authenticates user and returns the token which uses to access to the API.
    """
    request_serializer = UserLoginRequest(data=request.data)

    if request_serializer.is_valid():
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
    else:
        return invalid_data_response(request_serializer)


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def restore_data(request):
    """
    Sends mail to restore user data.
    """
    request_serializer = RestoreDataRequest(data=request.data)

    if request_serializer.is_valid():
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
    else:
        return invalid_data_response(request_serializer)


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def is_user_exists(request):
    """
    Checks if user is exists. If exists return True, else False.
    """
    request_serializer = UserExistsRequest(data=request.data)

    if request_serializer.is_valid():
        try:
            User.objects.get(username=request.data.get('username'))
            return Response({'status': 200,
                             'detail': 'successful',
                             'data': {'user': True}})

        except ObjectDoesNotExist:
            return Response({'status': 200,
                             'detail': 'successful',
                             'data': {'user': False}})
    else:
        return invalid_data_response(request_serializer)


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def is_mail_exists(request):
    """
    Checks if mail is exists. If exists return True, else False.
    """
    request_serializer = EmailExistsRequest(data=request.data)

    if request_serializer.is_valid():
        try:
            User.objects.get(email=request.data.get('email'))
            return Response({'status': 200,
                             'detail': 'successful',
                             'data': {'email': True}})

        except ObjectDoesNotExist:
            return Response({'status': 200,
                             'detail': 'successful',
                             'data': {'email': False}})
    else:
        return invalid_data_response(request_serializer)


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def sign_in(request):
    """
    Creates a new user and returns status.
    """
    request_serializer = SignInRequest(data=request.data)

    if request_serializer.is_valid():
        with transaction.atomic():
            if 'admin' in request.data.get('username'):
                return Response({'status': 400,
                                 'detail': 'not allowed username',
                                 'data': {}})

            user = User.objects.create_user(username=request.data.get('username'),
                                            email=request.data.get('email'),
                                            password=request.data.get('passw1'))
            user_token = TheUser.objects.get(id_user=user).auth_token

            logger.info("Created user with name: '{}' mail: '{}' and id: '{}'".format(user.username, user.email, user.id))
            login(request, user)

            successful_registration.delay(user.username, user.email)

            return Response({'status': 200,
                             'detail': 'successful',
                             'data': {'token': user_token}})
    else:
        return invalid_data_response(request_serializer)
