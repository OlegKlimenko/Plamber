# -*- coding: utf-8 -*-

import logging

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..serializers import CategorySerializer, BookSerializer
from app.models import TheUser, Category, Book

OUTPUT_BOOKS_PER_PAGE = 20

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def all_categories(request):
    """
    Generates the categories list.
    """
    get_object_or_404(TheUser, auth_token=request.data.get('user_token'))
    categories = Category.objects.all().order_by('category_name')

    return Response({'status': 200,
                     'detail': 'successful',
                     'data': [CategorySerializer(category, context={'request': request}).data
                              for category in categories]})


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def selected_category(request):
    """
    Returns books from selected category.
    """
    user = get_object_or_404(TheUser, auth_token=request.data.get('user_token'))
    category = get_object_or_404(Category, id=request.data.get('category_id'))

    books = Book.objects.filter(id_category=category).order_by('book_name')
    filtered_books = Book.exclude_private_books(user.id_user, books)

    paginator = Paginator(filtered_books, OUTPUT_BOOKS_PER_PAGE)
    page = paginator.page(request.data.get('page'))
    next_page = page.has_next()
    page_books = page.object_list

    return Response({'status': 200,
                     'detail': 'successful',
                     'data': {'books': [BookSerializer(book).data for book in page_books],
                              'next_page': page.next_page_number() if next_page else 0}})


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def find_book(request):
    """
    Generates list with books of data which user entered. At first it check full equality in name,
    after tries to check if contains some part of entered data.
    """
    user = get_object_or_404(TheUser, auth_token=request.data.get('user_token'))
    search_data = request.data.get('search_term')

    filtered_books = Book.exclude_private_books(user.id_user, Book.fetch_books(search_data))

    paginator = Paginator(filtered_books, OUTPUT_BOOKS_PER_PAGE)
    page = paginator.page(request.data.get('page'))
    next_page = page.has_next()
    page_books = page.object_list

    return Response({'status': 200,
                     'detail': 'successful',
                     'data': {'books': [BookSerializer(book).data for book in page_books],
                              'next_page': page.next_page_number() if next_page else 0}})
