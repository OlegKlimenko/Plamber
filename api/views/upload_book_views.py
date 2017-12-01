# -*- coding: utf-8 -*-

import logging

from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..serializers import BookSerializer
from app.models import Author, Book, TheUser

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


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def generate_books(request):
    """
    Returns a list of books which have a substring passed as param.
    """
    get_object_or_404(TheUser, auth_token=request.data.get('user_token'))
    list_of_books = Book.objects.filter(book_name__icontains=request.data.get('book_part'), private_book=False)

    return Response({'status': '200',
                     'detail': 'successful',
                     'data': [BookSerializer(book).data for book in list_of_books]})
