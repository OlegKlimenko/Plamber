# -*- coding: utf-8 -*-

import logging

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..serializers.request_serializers import SaveSupportMessageRequest
from ..utils import invalid_data_response, validate_api_secret_key
from app.models import SupportMessage

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def save_support_message(request):
    """
    Saves a support message if validated.
    """
    validate_api_secret_key(request.data.get('app_key'))
    request_serializer = SaveSupportMessageRequest(data=request.data)

    if request_serializer.is_valid():
        message = request.data.get('text')

        SupportMessage.objects.create(email=request.data.get('email'), text=message)

        return Response({'detail': 'successful',
                         'data': {}},
                        status=status.HTTP_200_OK)
    else:
        return invalid_data_response(request_serializer)
