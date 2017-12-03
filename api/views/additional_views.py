# -*- coding: utf-8 -*-

import logging

from rest_framework.decorators import api_view
from rest_framework.response import Response

from app.models import SupportMessage

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def save_support_message(request):
    """
    Saves a support message if validated.
    """
    message = request.data.get('text')

    if len(message) > 5000:
        return Response({'status': 400,
                         'detail': 'message length more than 5000 symbols',
                         'data': {}})

    SupportMessage.objects.create(email=request.data.get('email'), text=message)
    
    return Response({'status': 200,
                     'detail': 'successful',
                     'data': {}})
