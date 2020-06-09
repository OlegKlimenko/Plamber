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
from ..views import process_method, process_ajax, process_form

READ_PRIVILEGES = 0o644

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
@process_method('GET', 404)
def add_book(request):
    """
    Returns a page for adding book.
    """
    if request.user.is_authenticated():
        categories = Category.objects.all().order_by('category_name')
        languages = Language.objects.all()

        return render(request, 'add_book.html', {'categories': categories, 'languages': languages})
    else:
        return redirect('index')


# ----------------------------------------------------------------------------------------------------------------------
@process_ajax(404)
@process_form('GET', GenerateAuthorsForm, 404)
def generate_authors(request, form):
    """
    Returns a list of authors.
    """
    list_of_authors = Author.get_authors_list(form.cleaned_data['part'], True)

    return HttpResponse(json.dumps(list_of_authors), content_type='application/json')


# ----------------------------------------------------------------------------------------------------------------------
@process_ajax(404)
@process_form('GET', GenerateBooksForm, 404)
def generate_books(request, form):
    """
    Returns a list of books.
    """
    list_of_books = Book.generate_existing_books(form.cleaned_data['part'])

    return HttpResponse(json.dumps(list_of_books), content_type='application/json')


# ----------------------------------------------------------------------------------------------------------------------
@process_method('POST', 404)
@process_form('POST', AddBookForm, 404)
def add_book_successful(request, form):
    """
    Creates new book object.
    """
    with transaction.atomic():
        related_data = Book.get_related_objects_for_create(request.user.id, form)

        book = Book.objects.create(
            book_name=form.cleaned_data['bookname'],
            id_author=related_data.author,
            id_category=related_data.category,
            description=form.cleaned_data['about'],
            language=related_data.lang,
            book_file=form.cleaned_data['bookfile'],
            who_added=related_data.user,
            private_book=form.cleaned_data['private']
        )
        AddedBook.objects.create(id_user=related_data.user, id_book=book)

        logger.info("User '{}' uploaded book with id: '{}' and name: '{}' on category: '{}'."
                    .format(related_data.user, book.id, book.book_name, related_data.category))

        os.chmod(book.book_file.path, READ_PRIVILEGES)
        compress_pdf_task.apply_async(args=(book.book_file.path, book.id), queue=Queues.default)

        return HttpResponse(reverse('book', kwargs={'book_id': book.id}), status=200)
