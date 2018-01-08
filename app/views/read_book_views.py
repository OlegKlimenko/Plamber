# -*- coding: utf-8 -*-

import json
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .selected_book_views import selected_book
from ..forms import SetCurrentPageForm
from ..models import Book, AddedBook, TheUser

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
def open_book(request, book_id):
    """
    Returns a page for reading book.
    """
    if request.user.is_authenticated():
        book = Book.objects.get(id=book_id)
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
        return redirect('index')


# ----------------------------------------------------------------------------------------------------------------------
def set_current_page(request):
    """
    Changes current readed page for book of user.
    """
    if request.is_ajax():
        pages_form = SetCurrentPageForm(request.POST)

        if pages_form.is_valid():
            with transaction.atomic():
                book = Book.objects.get(id=pages_form.cleaned_data['book'])
                user = TheUser.objects.get(id_user=request.user)

                added_book = AddedBook.objects.get(id_book=book, id_user=user)
                added_book.last_page = pages_form.cleaned_data['page']
                added_book.save()

                logger.info("User '{}' on book with id: '{}' changed page to: '{}'."
                            .format(user, book.id, pages_form.cleaned_data['page']))

                return HttpResponse(json.dumps(True), content_type='application/json')
    else:
        return HttpResponse(status=404)
