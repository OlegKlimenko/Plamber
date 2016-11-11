# -*- coding: utf-8 -*-
import json

from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import RequestContext, loader

from ..forms import SetCurrentPageForm
from ..models import Book, AddedBook, TheUser


# ----------------------------------------------------------------------------------------------------------------------
def open_book_view(request, book_id):
    """
    Returns a page for reading book.

    :param django.core.handlers.wsgi.WSGIRequest request: The request for reading book.
    :param int book_id: The id of an opened book.
    :return: Page for reading book.
    """
    if request.user.is_authenticated():
        book = Book.objects.get(id=book_id)
        user = TheUser.objects.get(id_user=request.user)
        added_book = AddedBook.objects.get(id_book=book, id_user=user)

        template = loader.get_template('read_book.html')
        context = RequestContext(request, {'book_name': book.book_name,
                                           'book_url': book.book_file,
                                           'book_page': added_book.last_page})

        return HttpResponse(template.render(context))
    else:
        return redirect('index')


# ----------------------------------------------------------------------------------------------------------------------
def set_current_page_view(request):
    """
    Changes current readed page for book of user.

    :param django.core.handlers.wsgi.WSGIRequest request: The request for reading book.
    """
    if request.is_ajax():
        pages_form = SetCurrentPageForm(request.POST)

        if pages_form.is_valid():
            with transaction.atomic():
                book = Book.objects.get(book_name=pages_form.cleaned_data['book'])
                user = TheUser.objects.get(id_user=request.user)

                added_book = AddedBook.objects.get(id_book=book, id_user=user)
                added_book.last_page = pages_form.cleaned_data['page']
                added_book.save()

                return HttpResponse(json.dumps(True), content_type='application/json')
    else:
        return HttpResponse(status=404)
