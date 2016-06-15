# -*- coding: utf-8 -*-

import json
from django.db.models import Avg, Count
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import RequestContext, loader

from app.forms import SortForm
from app.models import Category, Book, BookRating, AddedBook


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
            category = Category.objects.get(id=sort_form.cleaned_data['category'])
            books = []

            if sort_form.cleaned_data['criterion'] == 'book_name':
                sort_by_book_name(books, category)

            elif sort_form.cleaned_data['criterion'] == 'author':
                sort_by_author(books, category)

            elif sort_form.cleaned_data['criterion'] == 'estimation':
                books = sort_by_estimation(books, category)

            elif sort_form.cleaned_data['criterion'] == 'most_readable':
                books = sort_by_readable(books, category)

            return HttpResponse(json.dumps(books), content_type='application/json')
    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def sort_by_book_name(books, category):
    """
    Sorts books by book name.

    :param list books: The final list with books.
    :param app.models.Category category: The category.
    """
    filtered_books = Book.objects.filter(id_category=category).order_by('book_name')

    generate_books(books, filtered_books)


# ----------------------------------------------------------------------------------------------------------------------
def sort_by_author(books, category):
    """
    Sorts books by author.

    :param list books: The final list with books.
    :param app.models.Category category: The category.
    """
    filtered_books = Book.objects.filter(id_category=category).order_by('id_author__author_name')

    generate_books(books, filtered_books)


# ----------------------------------------------------------------------------------------------------------------------
def generate_books(books, filtered_books):
    """
    Generates list with books for specific data and special criterion.

    :param list books: The final list with books.
    :param list filtered_books: The list of books after fetching them from database.
    :return:
    """
    for item in filtered_books:
        book = {'id': item.id, 'name': item.book_name, 'author': item.id_author.author_name}
        books.append(book)


# ----------------------------------------------------------------------------------------------------------------------
def sort_by_estimation(books, category):
    """
    Sorts books by average count of estimation of each book. Uses aggregate function.

    :param list books: The final list with books.
    :param app.models.Category category: The category.

    :return: The list with sorted books.
    """
    filtered_books = Book.objects.filter(id_category=category)

    for item in filtered_books:
        book_rating = BookRating.objects.filter(id_book=item).aggregate(Avg('rating'))
        book = {'id': item.id,
                'name': item.book_name,
                'author': item.id_author.author_name,
                'rating': book_rating['rating__avg']}
        books.append(book)

    return sorted(books, key=lambda info: (info['rating'] is not None, info['rating']), reverse=True)


# ----------------------------------------------------------------------------------------------------------------------
def sort_by_readable(books, category):
    """

    Sorts books by most readable criterion. Uses aggregate 'count' function.

    :param list books: The final list with books.
    :param app.models.Category category: The category.

    :return: The list with sorted books.
    """
    filtered_books = Book.objects.filter(id_category=category)

    for item in filtered_books:
        book_read_count = AddedBook.objects.filter(id_book=item).aggregate(Count('id_user'))
        book = {'id': item.id,
                'name': item.book_name,
                'author': item.id_author.author_name,
                'read_count': book_read_count['id_user__count']}
        books.append(book)

    return sorted(books, key=lambda info: info['read_count'], reverse=True)
