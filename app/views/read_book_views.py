# -*- coding: utf-8 -*-

import json
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from .selected_book_views import selected_book
from ..forms import SetCurrentPageForm
from ..models import Book, AddedBook, TheUser
from ..views import process_ajax, process_form

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
def open_book(request, book_id):
    """
    Returns a page for reading book.
    """
    book = get_object_or_404(Book, id=book_id)

    if request.user.is_authenticated():
        user = TheUser.objects.get(id_user=request.user)

        try:
            added_book = AddedBook.objects.get(id_book=book, id_user=user)
            added_book.last_read = added_book.last_read.now()
            added_book.save()

            logger.info("User '{}' opened book with id: '{}'.".format(user, book.id))
            context = {'book': book, 'book_page': added_book.last_page}
            return render(request, 'read_book.html', context)

        except ObjectDoesNotExist:
            return redirect(selected_book, book_id=book_id)
    else:
        if book.blocked_book:
            return redirect(selected_book, book_id=book_id)
        if book.private_book:
            return HttpResponse(status=404)

        try:
            book_page = int(request.COOKIES.get('plamber_book_{}'.format(book_id), 1))
        except ValueError:
            book_page = 1

        context = {'book': book, 'book_page': book_page}
        return render(request, 'read_book.html', context)


# ----------------------------------------------------------------------------------------------------------------------
@process_ajax(404)
@process_form('POST', SetCurrentPageForm, 404)
def set_current_page(request, form):
    """
    Changes current readed page for book of user.
    """
    with transaction.atomic():
        book = Book.objects.get(id=form.cleaned_data['book'])
        user = TheUser.objects.get(id_user=request.user)

        added_book = AddedBook.objects.get(id_book=book, id_user=user)
        added_book.last_page = form.cleaned_data['page']
        added_book.save()

        logger.info("User '{}' on book with id: '{}' changed page to: '{}'."
                    .format(user, book.id, form.cleaned_data['page']))

        return HttpResponse(json.dumps(True), content_type='application/json')
