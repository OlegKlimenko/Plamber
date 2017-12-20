# -*- coding: utf-8 -*-

import logging

from django.db import transaction
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from ..serializers.model_serializers import ProfileSerializer
from app.models import TheUser
from app.tasks import changed_password
from app.utils import resize_image

AVATAR_WIDTH = 250

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def my_profile(request):
    """
    Generates the user profile data.
    """
    the_user = get_object_or_404(TheUser, auth_token=request.data.get('user_token'))

    return Response({'status': 200,
                     'detail': 'successful',
                     'data': {'profile': ProfileSerializer(the_user).data}})


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def change_password(request):
    """
    Changes user password.
    """
    the_user = get_object_or_404(TheUser, auth_token=request.data.get('user_token'))

    with transaction.atomic():
        if the_user.id_user.check_password(request.data.get('prev_password')):
            the_user.id_user.set_password(request.data.get('new_password'))
            the_user.id_user.save()

            logger.info("User '{}' changed his password successfully.".format(the_user.id_user))

            changed_password.delay(the_user.id_user.username, the_user.id_user.email)

            return Response({'status': 200,
                             'detail': 'successful',
                             'data': {}})

        else:
            return Response({'status': 200,
                             'detail': 'old password didn\'t match',
                             'data': {}})


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
@parser_classes((MultiPartParser,))
def upload_avatar(request):
    """
    Sets new user's avatar.
    """
    with transaction.atomic():
        profile_user = get_object_or_404(TheUser, auth_token=request.data.get('user_token'))

        try:
            profile_user.user_photo.save('user_{}.png'.format(profile_user.id), request.data.get('file'))
            profile_user.save()
            logger.info("User '{}' changed his avatar.".format(profile_user))

            resize_image(profile_user.user_photo.path, AVATAR_WIDTH)
            logger.info("Image '{}' successfully resized!".format(profile_user.user_photo.path))

            return Response({'status': 200,
                             'detail': 'successful',
                             'data': {'profile_image': profile_user.user_photo.url}})

        except ValidationError:
            logger.info("User '{}' tried to upload not an image as avatar!".format(profile_user))

            return Response({'status': 404,
                             'detail': 'tried to upload not an image',
                             'data': {}})
