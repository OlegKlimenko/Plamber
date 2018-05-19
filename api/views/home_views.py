# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..serializers.model_serializers import BookSerializer
from ..serializers.request_serializers import HomeRequest
from ..utils import invalid_data_response, validate_api_secret_key
from app.models import TheUser, AddedBook, Book
from app.recommend import get_recommend

RANDOM_BOOKS_COUNT = 6


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def home(request):
    """
    Generates user home data (i.e. user's added books).
    """
    validate_api_secret_key(request.data.get('app_key'))
    request_serializer = HomeRequest(data=request.data)

    if request_serializer.is_valid():
        the_user = get_object_or_404(TheUser, auth_token=request.data.get('user_token'))
        books = [book.id_book for book in AddedBook.get_user_added_books(the_user.id_user)]

        return Response({'detail': 'successful',
                         'data': [BookSerializer(book).data for book in books]},
                        status=status.HTTP_200_OK)
    else:
        return invalid_data_response(request_serializer)


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def recommendations(request):
    """
    Generates recommend books data.
    """
    validate_api_secret_key(request.data.get('app_key'))
    request_serializer = HomeRequest(data=request.data)

    if request_serializer.is_valid():
        the_user = get_object_or_404(TheUser, auth_token=request.data.get('user_token'))

        added_books = AddedBook.get_user_added_books(the_user.id_user)
        recommend_books = get_recommend(the_user.id_user, added_books, RANDOM_BOOKS_COUNT, [])

        return Response({'detail': 'successful',
                         'data': [BookSerializer(book).data for book in recommend_books]},
                        status=status.HTTP_200_OK)
    else:
        return invalid_data_response(request_serializer)


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def uploaded_books(request):
    """
    Returns the list of books which user uploaded before in system.
    """
    validate_api_secret_key(request.data.get('app_key'))
    request_serializer = HomeRequest(data=request.data)

    if request_serializer.is_valid():
        the_user = get_object_or_404(TheUser, auth_token=request.data.get('user_token'))
        user_uploaded_books = Book.objects.filter(who_added=the_user).order_by('-id')

        return Response({'detail': 'successful',
                         'data': [BookSerializer(book).data for book in user_uploaded_books]},
                        status=status.HTTP_200_OK)
    else:
        return invalid_data_response(request_serializer)
