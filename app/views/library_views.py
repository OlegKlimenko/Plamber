# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.html import escape

from ..forms import SortForm, SearchBookForm
from ..models import Category, Book


# ----------------------------------------------------------------------------------------------------------------------
def all_categories(request):
    """
    Returns page with book categories.
    """
    if request.method == "GET":
        if request.user.is_authenticated():
            categories = Category.objects.all().order_by('category_name')

            count = categories.count() / 2

            first_line = categories[:count+1]
            second_line = categories[count+1:count*2]

            return render(request, 'categories.html', {'first_line': first_line,
                                                       'second_line': second_line})

        else:
            return redirect('index')


# ----------------------------------------------------------------------------------------------------------------------
def selected_category(request, category_id):
    """
    Returns page with selected category.
    """
    if request.method == 'GET':
        if request.user.is_authenticated():
            category = Category.objects.get(id=category_id)
            books = Book.objects.filter(id_category=category).order_by('book_name')

            filtered_books = Book.exclude_private_books(request.user, books)

            context = {'category': category, 'books': filtered_books, 'category_number': category_id}
            return render(request, 'selected_category.html', context)

        else:
            return redirect('index')


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
