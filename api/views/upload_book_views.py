# -*- coding: utf-8 -*-

import logging

from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response

from app.models import Author, TheUser

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def generate_authors(request):
    """
    Returns a list of authors which have a substring passed as param.
    """
    get_object_or_404(TheUser, auth_token=request.data.get('user_token'))
    list_of_authors = Author.get_authors_list(request.data.get('author_part'))

    return Response({'status': '200',
                     'detail': 'successful',
                     'data': list_of_authors})
