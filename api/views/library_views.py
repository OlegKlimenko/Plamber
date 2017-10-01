# -*- coding: utf-8 -*-

import logging

from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..serializers import CategorySerializer
from app.models import TheUser, Category

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def all_categories(request):
    """
    Generates the categories list.
    """
    the_user = get_object_or_404(TheUser, auth_token=request.data.get('user_token'))
    categories = Category.objects.all().order_by('category_name')

    return Response({'status': 200,
                     'detail': 'successful',
                     'data': [CategorySerializer(category, context={'request': request}).data
                              for category in categories]})


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def selected_category(request, category_id):
    """
    Returns books from selected category.
    """
    pass
