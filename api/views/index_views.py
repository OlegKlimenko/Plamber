# -*- coding: utf-8 -*-

import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from app.constants import Queues
from app.models import TheUser
from app.tasks import restore_account, successful_registration
from app.utils import generate_password
from ..utils import invalid_data_response, validate_api_secret_key
from ..serializers.request_serializers import (UserLoginUsernameRequest,
                                               UserLoginEmailRequest,
                                               RestoreDataRequest,
                                               UserExistsRequest,
                                               EmailExistsRequest,
                                               SignInRequest)

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
def login_response(request, username):
    """
    Authenticates user and returns the token with the appropriate
    status for the authenticated and not authenticated users.
    """
    user = authenticate(username=username, password=request.data.get('password'))

    if user:
        user_token = TheUser.objects.get(id_user=user).auth_token

        login(request, user)
        logger.info("User '{}' logged in.".format(user.username))

        return Response({'detail': 'successful',
                         'data': {'token': user_token}},
                        status=status.HTTP_200_OK)

    return Response({'detail': 'not authenticated',
                     'data': {'token': None}},
                    status=status.HTTP_404_NOT_FOUND)

# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def user_login(request):
    """
    Validates request data and logs user.
    """
    validate_api_secret_key(request.data.get('app_key'))

    username_request_serializer = UserLoginUsernameRequest(data=request.data)
    email_request_serializer = UserLoginEmailRequest(data=request.data)

    if email_request_serializer.is_valid():
        user_obj = User.objects.filter(email=request.data.get('username'))
        username = user_obj[0] if len(user_obj) else None

        return login_response(request, username)

    elif username_request_serializer.is_valid():
        return login_response(request, request.data.get('username'))

    return invalid_data_response(username_request_serializer)


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def restore_data(request):
    """
    Sends mail to restore user data.
    """
    validate_api_secret_key(request.data.get('app_key'))
    request_serializer = RestoreDataRequest(data=request.data)

    if request_serializer.is_valid():
        with transaction.atomic():
            temp_password = generate_password()

            try:
                user = User.objects.get(email=request.data.get('email'))
                user.set_password(temp_password)
                user.save()

                restore_account.apply_async(
                    args=(user.username, temp_password, request.data.get('email')), queue=Queues.high_priority
                )

                logger.info("The password for user: '{}' restored successfully.".format(user))

                return Response({'detail': 'successful',
                                 'data': {}},
                                status=status.HTTP_200_OK)

            except ObjectDoesNotExist:
                return Response({'detail': 'not exists',
                                 'data': {}},
                                status=status.HTTP_404_NOT_FOUND)
    else:
        return invalid_data_response(request_serializer)


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def is_user_exists(request):
    """
    Checks if user is exists. If exists return True, else False.
    """
    validate_api_secret_key(request.data.get('app_key'))
    request_serializer = UserExistsRequest(data=request.data)

    if request_serializer.is_valid():
        try:
            User.objects.get(username=request.data.get('username'))
            return Response({'detail': 'successful',
                             'data': {'user': True}},
                            status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'detail': 'successful',
                             'data': {'user': False}},
                            status=status.HTTP_200_OK)
    else:
        return invalid_data_response(request_serializer)


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def is_mail_exists(request):
    """
    Checks if mail is exists. If exists return True, else False.
    """
    validate_api_secret_key(request.data.get('app_key'))
    request_serializer = EmailExistsRequest(data=request.data)

    if request_serializer.is_valid():
        try:
            User.objects.get(email=request.data.get('email'))
            return Response({'detail': 'successful',
                             'data': {'email': True}},
                            status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'detail': 'successful',
                             'data': {'email': False}},
                            status=status.HTTP_200_OK)
    else:
        return invalid_data_response(request_serializer)


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def sign_in(request):
    """
    Creates a new user and returns status.
    """
    validate_api_secret_key(request.data.get('app_key'))
    request_serializer = SignInRequest(data=request.data)

    if request_serializer.is_valid():
        with transaction.atomic():
            if 'admin' in request.data.get('username'):
                return Response({'detail': 'not allowed username',
                                 'data': {}},
                                status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create_user(username=request.data.get('username'),
                                            email=request.data.get('email'),
                                            password=request.data.get('passw1'))
            user_token = TheUser.objects.get(id_user=user).auth_token

            logger.info(
                "Created user with name: '{}' mail: '{}' and id: '{}'".format(user.username, user.email, user.id)
            )
            login(request, user)

            successful_registration.apply_async(args=(user.username, user.email), queue=Queues.default)

            return Response({'detail': 'successful',
                             'data': {'token': user_token}},
                            status=status.HTTP_200_OK)
    else:
        return invalid_data_response(request_serializer)
