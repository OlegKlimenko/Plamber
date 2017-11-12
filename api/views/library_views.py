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
    the_user = get_object_or_404(TheUser, auth_token=request.data.get('user_token'))
    categories = Category.objects.all().order_by('category_name')

    return Response({'status': 200,
                     'detail': 'successful',
                     'data': [CategorySerializer(category, context={'request': request}).data
                              for category in categories]})


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def selected_category(request, category_id):
    """
    Returns books from selected category.
    """
    the_user = get_object_or_404(TheUser, auth_token=request.data.get('user_token'))

    category = Category.objects.get(id=category_id)
    books = Book.objects.filter(id_category=category).order_by('book_name')
    filtered_books = Book.exclude_private_books(request.user, books)

    paginator = Paginator(filtered_books, OUTPUT_BOOKS_PER_PAGE)
    page = paginator.page(request.data.get('page'))
    next_page = page.has_next()
    page_books = page.object_list

    return Response({'status': 200,
                     'detail': 'successful',
                     'data': {'books': [BookSerializer(book).data for book in page_books],
                              'next_page': page.next_page_number() if next_page else next_page}})
