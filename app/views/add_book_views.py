# -*- coding: utf-8 -*-

import json
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render

from ..forms import GenerateAuthorsForm, AddBookForm
from ..models import Author, Book, Category, Language


# ----------------------------------------------------------------------------------------------------------------------
def add_book_view(request):
    """
    Returns a page for adding book.

    :param django.core.handlers.wsgi.WSGIRequest request: The request for adding book.
    :return: Page for adding book
    """
    if request.method == 'GET':
        if request.user.is_authenticated():
            categories = Category.objects.all()
            languages = Language.objects.all()

            return render(request, 'add_book.html', {'categories': categories, 'languages': languages})
        else:
            return redirect('index')


# ----------------------------------------------------------------------------------------------------------------------
def generate_authors_view(request):
    """
    Returns a list of authors.

    :param django.core.handlers.wsgi.WSGIRequest request: The request for generating list of possible authors.
    :return: A list of authors.
    """
    if request.is_ajax():
        authors_form = GenerateAuthorsForm(request.GET)

        if authors_form.is_valid():
            list_of_authors = Author.get_authors_list(authors_form.cleaned_data['part'])
            return HttpResponse(json.dumps(list_of_authors), content_type='application/json')
    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def add_book_successful_view(request):
    """
    Creates new book object.

    :param django.core.handlers.wsgi.WSGIRequest request: The request for adding new book.
    :return: A page with added book.
    """
    if request.method == 'POST':
        book_form = AddBookForm(request.POST, request.FILES)

        if book_form.is_valid():
            with transaction.atomic():
                rel_objects = Book.get_related_objects_for_create(request.user.id, book_form)

                book = Book.objects.create(book_name=book_form.cleaned_data['bookname'],
                                           id_author=rel_objects['author'],
                                           id_category=rel_objects['category'],
                                           description=book_form.cleaned_data['about'],
                                           language=rel_objects['lang'],
                                           book_file=book_form.cleaned_data['bookfile'],
                                           who_added=rel_objects['user'])
                return redirect('book/{0}/'.format(book.id))
    else:
        return HttpResponse(status=404)
