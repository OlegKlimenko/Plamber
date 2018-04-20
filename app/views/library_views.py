# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.html import escape

from ..forms import SortForm, SearchBookForm
from ..models import Category, Book


# ----------------------------------------------------------------------------------------------------------------------
def all_categories(request):
    """
    Returns page with book categories.
    """
    if request.method == "GET":
        categories = Category.objects.all().order_by('category_name')
        # most_readable_books = Book.sort_by_readable(request.user)

        return render(request, 'categories.html', {'categories': categories})
                                                   # 'most_readable_books': most_readable_books[:9]})
    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def selected_category(request, category_id):
    """
    Returns page with selected category.
    """
    if request.method == 'GET':
        category = get_object_or_404(Category, id=category_id)
        books = Book.objects.filter(id_category=category).order_by('book_name')

        filtered_books = Book.exclude_private_books(request.user, books)

        context = {'category': category, 'books': filtered_books, 'category_number': category_id}
        return render(request, 'selected_category.html', context)

    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def sort(request):
    """
    Returns data sorted data depending on criterion.
    """
    if request.is_ajax():
        sort_form = SortForm(request.GET)

        if sort_form.is_valid():
            criterion_dict = {'book_name': Book.sort_by_book_name,
                              'author': Book.sort_by_author,
                              'estimation': Book.sort_by_estimation,
                              'most_readable': Book.sort_by_readable}

            category = Category.objects.get(id=sort_form.cleaned_data['category'])
            books = criterion_dict[sort_form.cleaned_data['criterion']](request.user, category)

            for book in books:
                book['name'] = escape(book['name'])
                book['author'] = escape(book['author'])

            return HttpResponse(json.dumps(books), content_type='application/json')
    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def find_books(request):
    """
    Generates list with books of data which user entered. At first it check full equality in name,
    after tries to check if contains some part of entered data.
    """
    if request.is_ajax():
        search_book_form = SearchBookForm(request.GET)

        if search_book_form.is_valid():
            search_data = search_book_form.cleaned_data['data']

            filtered_books = Book.exclude_private_books(request.user, Book.fetch_books(search_data))
            books = Book.generate_books(filtered_books)

            for book in books:
                book['name'] = escape(book['name'])
                book['author'] = escape(book['author'])

            return HttpResponse(json.dumps(books), content_type='application/json')
    else:
        return HttpResponse(status=404)
