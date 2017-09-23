# -*- coding: utf-8 -*-

import logging

from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..serializers import BookSerializer, ProfileSerializer
from app.models import TheUser, AddedBook, Book
from app.tasks import changed_password

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

            changed_password.delay(request.user.username, request.user.email)

            return Response({'status': 200,
                             'detail': 'successful',
                             'data': {}})

        else:
            return Response({'status': 200,
                             'detail': 'old password didn\'t match',
                             'data': {}})
