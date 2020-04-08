# -*- coding: utf-8 -*-

import json
import logging
import os

from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render, reverse

from ..constants import Queues
from ..forms import GenerateAuthorsForm, AddBookForm, GenerateBooksForm
from ..models import AddedBook, Author, Book, Category, Language
from ..tasks import compress_pdf_task

READ_PRIVILEGES = 0o644

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
def add_book(request):
    """
    Returns a page for adding book.
    """
    if request.method == 'GET':
        if request.user.is_authenticated():
            categories = Category.objects.all().order_by('category_name')
            languages = Language.objects.all()

            return render(request, 'add_book.html', {'categories': categories, 'languages': languages})
        else:
            return redirect('index')


# ----------------------------------------------------------------------------------------------------------------------
def generate_authors(request):
    """
    Returns a list of authors.
    """
    if request.is_ajax():
        authors_form = GenerateAuthorsForm(request.GET)

        if authors_form.is_valid():
            list_of_authors = Author.get_authors_list(authors_form.cleaned_data['part'], True)

            return HttpResponse(json.dumps(list_of_authors), content_type='application/json')
        else:
            return HttpResponse(status=404)
    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def generate_books(request):
    """
    Returns a list of books.
    """
    if request.is_ajax():
        book_list_form = GenerateBooksForm(request.GET)

        if book_list_form.is_valid():
            list_of_books = Book.generate_existing_books(book_list_form.cleaned_data['part'])

            return HttpResponse(json.dumps(list_of_books), content_type='application/json')
        else:
            return HttpResponse(status=404)

    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def add_book_successful(request):
    """
    Creates new book object.
    """
    if request.method == 'POST':
        book_form = AddBookForm(request.POST, request.FILES)

        if book_form.is_valid():
            with transaction.atomic():
                related_data = Book.get_related_objects_for_create(request.user.id, book_form)

                book = Book.objects.create(
                    book_name=book_form.cleaned_data['bookname'],
                    id_author=related_data.author,
                    id_category=related_data.category,
                    description=book_form.cleaned_data['about'],
                    language=related_data.lang,
                    book_file=book_form.cleaned_data['bookfile'],
                    who_added=related_data.user,
                    private_book=book_form.cleaned_data['private']
                )
                AddedBook.objects.create(id_user=related_data.user, id_book=book)

                logger.info("User '{}' uploaded book with id: '{}' and name: '{}' on category: '{}'."
                            .format(related_data.user, book.id, book.book_name, related_data.category))

                os.chmod(book.book_file.path, READ_PRIVILEGES)
                compress_pdf_task.apply_async(args=(book.book_file.path, book.id), queue=Queues.default)

                return HttpResponse(reverse('book', kwargs={'book_id': book.id}), status=200)
        else:
            return HttpResponse(status=404)
    else:
        return HttpResponse(status=404)
