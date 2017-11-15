# -*- coding: utf-8 -*-

import logging

from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response

from app.models import Book, AddedBook, TheUser

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def open_book(request):
    """
    Returns the book of last readed page.
    """
    user = get_object_or_404(TheUser, auth_token=request.data.get('user_token'))
    book = get_object_or_404(Book, id=request.data.get('book_id'))

    added_book = get_object_or_404(AddedBook, id_book=book, id_user=user)
    added_book.last_read = added_book.last_read.now()
    added_book.save()

    logger.info("User '{}' opened book with id: '{}'.".format(user, book.id))

    return Response({'status': 200,
                     'detail': 'successful',
                     'data': {'last_page': added_book.last_page}})
