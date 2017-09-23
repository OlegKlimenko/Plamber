# -*- coding: utf-8 -*-

import logging

from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..serializers import BookSerializer, ProfileSerializer
from app.models import TheUser, AddedBook, Book

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def my_profile(request):
    """
    Generates the user profile data.
    """
    the_user = get_object_or_404(TheUser, auth_token=request.data.get('user_token'))

    added_books = [book.id_book for book in AddedBook.get_user_added_books(the_user.id_user)]
    uploaded_books = Book.objects.filter(who_added=the_user).order_by('-id')

    return Response({'status': 200,
                     'detail': 'successful',
                     'data': {'profile': ProfileSerializer(the_user).data,
                              'added_books': [BookSerializer(book).data for book in added_books],
                              'uploaded_books': [BookSerializer(book).data for book in uploaded_books]}})
