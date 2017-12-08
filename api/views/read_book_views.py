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


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def set_current_page(request):
    """
    Changes current readed page for book of the user.
    """
    user = get_object_or_404(TheUser, auth_token=request.data.get('user_token'))
    book = get_object_or_404(Book, id=request.data.get('book_id'))
    current_page = request.data.get('current_page')

    if not isinstance(current_page, int):
        return Response({'status': 400,
                         'detail': 'current page not a number',
                         'data': {}}, status=400)

    added_book = AddedBook.objects.get(id_book=book, id_user=user)
    added_book.last_page = current_page
    added_book.save()

    logger.info("User '{}' on book with id: '{}' changed page to: '{}'."
                .format(user, book.id, current_page))

    return Response({'status': 200,
                     'detail': 'successful',
                     'data': {}})
