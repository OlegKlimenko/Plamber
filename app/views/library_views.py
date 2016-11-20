# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import RequestContext, loader

from ..forms import SortForm, SearchBookForm
from ..models import Category, Book


# ----------------------------------------------------------------------------------------------------------------------
def categories_view(request):
    """
    Returns page with book categories.

    :param django.core.handlers.wsgi.WSGIRequest request: The request on categories page.
    :return: The HTML page.
    """
    if request.method == "GET":
        if request.user.is_authenticated():
            categories = Category.objects.all().order_by('category_name')

            template = loader.get_template('categories.html')
            context = RequestContext(request, {'categories': categories})
            return HttpResponse(template.render(context))
        else:
            return redirect('index')


# ----------------------------------------------------------------------------------------------------------------------
def selected_category_view(request, category_id):
    """
    Returns page with selected category.

    :param django.core.handlers.wsgi.WSGIRequest request: The request on selected category page.
    :param str category_id: The identifier of a category.
    :return: The HTML page.
    """
    if request.method == 'GET':
        if request.user.is_authenticated():
            category = Category.objects.get(id=category_id)
            books = Book.objects.filter(id_category=category).order_by('book_name')

            template = loader.get_template('selected_category.html')
            context = RequestContext(request, {'category_name': category.category_name,
                                               'category_number': category.id,
                                               'books': books})
            return HttpResponse(template.render(context))

        else:
            return redirect('index')


# ----------------------------------------------------------------------------------------------------------------------
def sort_view(request):
    """
    Returns data sorted data depending on criterion.

    :param django.core.handlers.wsgi.WSGIRequest request: The request for sorting.
    :return: The sorted objects.
    """
    if request.is_ajax():
        sort_form = SortForm(request.GET)

        if sort_form.is_valid():
            criterion_dict = {'book_name': Book.sort_by_book_name,
                              'author': Book.sort_by_author,
                              'estimation': Book.sort_by_estimation,
                              'most_readable': Book.sort_by_readable}

            category = Category.objects.get(id=sort_form.cleaned_data['category'])

            books = criterion_dict[sort_form.cleaned_data['criterion']](category)
            return HttpResponse(json.dumps(books), content_type='application/json')
    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def find_books(request):
    """
    Generates list with books of data which user entered. At first it check full equality in name,
    after tries to check if contains some part of entered data.

    :param django.core.handlers.wsgi.WSGIRequest request: The request for searching.
    :return: The list of books.
    """
    if request.is_ajax():
        search_book_form = SearchBookForm(request.GET)

        if search_book_form.is_valid():
            search_data = search_book_form.cleaned_data['data']

            filtered_books = Book.fetch_books(search_data)
            books = Book.generate_books(filtered_books)

            return HttpResponse(json.dumps(books), content_type='application/json')
    else:
        return HttpResponse(status=404)
