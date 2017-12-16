# -*- coding: utf-8 -*-

import json
import logging

from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from ..serializers import BookSerializer
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
    with transaction.atomic():
        user = get_object_or_404(TheUser, auth_token=request.data.get('user_token'))
        rel_objects = Book.get_related_objects_create_api(user, request.data)

        book = Book.objects.create(book_name=request.data.get('book_name'),
                                   id_author=rel_objects['author'],
                                   id_category=rel_objects['category'],
                                   description=request.data.get('about'),
                                   language=rel_objects['lang'],
                                   book_file=request.data['book_file'],
                                   who_added=user,
                                   private_book=json.loads(request.data.get('private_book')))

        AddedBook.objects.create(id_user=user, id_book=book)

        logger.info("User '{}' uploaded book with id: '{}' and name: '{}' on category: '{}'."
                    .format(user, book.id, book.book_name, rel_objects['category']))

        compress_pdf_task.delay(book.book_file.path)

        return Response({'status': '200',
                         'detail': 'successful',
                         'data': {}})


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


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def generate_languages(request):
    """
    Returns the languages list.
    """
    get_object_or_404(TheUser, auth_token=request.data.get('user_token'))
    list_of_languages = Language.objects.all()

    return Response({'status': '200',
                     'detail': 'successful',
                     'data': [language.language for language in list_of_languages]})
