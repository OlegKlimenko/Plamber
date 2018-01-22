# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.http import Http404

from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
def invalid_data_response(request_serializer):
    """
    Returns the error message depending on missing/invalid data in serializer.
    """
    return Response({'detail': request_serializer.errors,
                     'data': {}}, status=status.HTTP_400_BAD_REQUEST)


# ----------------------------------------------------------------------------------------------------------------------
def validate_api_secret_key(secret_key):
    """
    Checks if request received from known origin Application. If not returns 404 (not found) status
    """
    if secret_key != settings.API_SECRET_KEY:
        logger.info('Incorrect API key: "{}"'.format(secret_key))
        raise Http404('The API key isn\t correct!')
