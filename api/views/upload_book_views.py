# -*- coding: utf-8 -*-

import json
import logging

from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from ..serializers.model_serializers import BookSerializer
from ..serializers.request_serializers import (UploadBookRequest,
                                               GenerateAuthorsRequest,
                                               GenerateBooksRequest,
                                               GenerateLanguagesRequest)
from ..utils import invalid_data_response, validate_api_secret_key

from app.constants import Queues
from app.models import Author, AddedBook, Book, TheUser, Language
from app.tasks import compress_pdf_task

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
@parser_classes((MultiPartParser,))
def upload_book(request):
    """
    Handles request and saves uploaded book.
    """
    validate_api_secret_key(request.data.get('app_key'))
    request_serializer = UploadBookRequest(data=request.data)

    if request_serializer.is_valid():
        with transaction.atomic():
            user = get_object_or_404(TheUser, auth_token=request.data.get('user_token'))
            related_data = Book.get_related_objects_create_api(user, request.data)

            book = Book.objects.create(
                book_name=request.data.get('book_name'),
                id_author=related_data.author,
                id_category=related_data.category,
                description=request.data.get('about'),
                language=related_data.lang,
                photo=request.data['photo'],
                book_file=request.data['book_file'],
                who_added=user,
                private_book=json.loads(request.data.get('private_book'))
            )
            AddedBook.objects.create(id_user=user, id_book=book)

            logger.info("User '{}' uploaded book with id: '{}' and name: '{}' on category: '{}'."
                        .format(user, book.id, book.book_name, related_data.category))

            compress_pdf_task.apply_async(args=(book.book_file.path, book.id), queue=Queues.default)

            return Response({'detail': 'successful',
                             'data': {'book': BookSerializer(book).data}},
                            status=status.HTTP_200_OK)
    else:
        return invalid_data_response(request_serializer)


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def generate_authors(request):
    """
    Returns a list of authors which have a substring passed as param.
    """
    validate_api_secret_key(request.data.get('app_key'))
    request_serializer = GenerateAuthorsRequest(data=request.data)

    if request_serializer.is_valid():
        get_object_or_404(TheUser, auth_token=request.data.get('user_token'))
        list_of_authors = Author.get_authors_list(request.data.get('author_part'))

        return Response({'detail': 'successful',
                         'data': list_of_authors},
                        status=status.HTTP_200_OK)
    else:
        return invalid_data_response(request_serializer)


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def generate_books(request):
    """
    Returns a list of books which have a substring passed as param.
    """
    validate_api_secret_key(request.data.get('app_key'))
    request_serializer = GenerateBooksRequest(data=request.data)

    if request_serializer.is_valid():
        get_object_or_404(TheUser, auth_token=request.data.get('user_token'))
        list_of_books = Book.objects.filter(book_name__icontains=request.data.get('book_part'), private_book=False)

        return Response({'detail': 'successful',
                         'data': [BookSerializer(book).data for book in list_of_books]},
                        status=status.HTTP_200_OK)
    else:
        return invalid_data_response(request_serializer)


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def generate_languages(request):
    """
    Returns the languages list.
    """
    validate_api_secret_key(request.data.get('app_key'))
    request_serializer = GenerateLanguagesRequest(data=request.data)

    if request_serializer.is_valid():
        get_object_or_404(TheUser, auth_token=request.data.get('user_token'))
        list_of_languages = Language.objects.all()

        return Response({'detail': 'successful',
                         'data': [language.language for language in list_of_languages]},
                        status=status.HTTP_200_OK)
    else:
        return invalid_data_response(request_serializer)
