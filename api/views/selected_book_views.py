# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..serializers import BookSerializer, CommentSerializer
from app.models import AddedBook, Book, TheUser


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
