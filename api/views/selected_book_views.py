# -*- coding: utf-8 -*-

import logging

from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..serializers import BookSerializer, CommentSerializer
from app.models import AddedBook, Book, BookComment, TheUser

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def selected_book(request):
    """
    Returns data for selected book.
    """
    user = get_object_or_404(TheUser, auth_token=request.data.get('user_token'))
    book_id = request.data.get('book_id')

    rel_objects = Book.get_related_objects_selected_book(request.user, book_id)

    if rel_objects['book'].private_book and rel_objects['book'].who_added != user:
        return Response({}, status=404)

    book_rating = rel_objects['avg_book_rating']['rating__avg']
    book_rating_count = rel_objects['book_rating_count']
    comments = [CommentSerializer(comment).data for comment in rel_objects['comments']]

    return Response({'status': 200,
                     'detail': 'success',
                     'data': {'book': BookSerializer(rel_objects['book']).data,
                              'is_added_book': bool(rel_objects['added_book']),
                              'user_reading_count': AddedBook.get_count_added(book_id),
                              'book_rating': book_rating if book_rating else 0,
                              'book_rated_count': book_rating_count if book_rating_count else 0,
                              'comments': comments}})


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def add_book_to_home(request):
    """
    Adds book to list of user's added books.
    """
    user = get_object_or_404(TheUser, auth_token=request.data.get('user_token'))
    book = get_object_or_404(Book, id=request.data.get('book_id'))

    if book.private_book and book.who_added != user:
        return Response({}, status=404)

    if AddedBook.objects.filter(id_user=user, id_book=book).exists():
        return Response({}, status=404)

    AddedBook.objects.create(id_user=user, id_book=book)
    logger.info("User '{}' added book with id: '{}' to his own library.".format(user.id_user.id, book.id))

    return Response({'status': 200,
                     'detail': 'success',
                     'data': {}})


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def remove_book_from_home(request):
    """
    Removes book from list of user's reading books.
    """
    user = get_object_or_404(TheUser, auth_token=request.data.get('user_token'))
    book = get_object_or_404(Book, id=request.data.get('book_id'))
    added_book = get_object_or_404(AddedBook, id_user=user, id_book=book)

    added_book.delete()
    logger.info("User '{}' removed book with id: '{}' from his own library."
                .format(request.user, request.data.get('book_id')))

    return Response({'status': 200,
                     'detail': 'success',
                     'data': {}})


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def add_comment(request):
    the_user = get_object_or_404(TheUser, auth_token=request.data.get('user_token'))

    comment = BookComment.objects.create(id_user=the_user,
                                         id_book=Book.objects.get(id=request.data.get('book_id')),
                                         text=request.data.get('text'))

    logger.info("User '{}' left comment with id: '{}' on book with id: '{}'."
                .format(the_user.id_user.id, comment.id, comment.id_book.id))

    return Response({'status': 200,
                     'detail': 'success',
                     'data': CommentSerializer(comment).data})
