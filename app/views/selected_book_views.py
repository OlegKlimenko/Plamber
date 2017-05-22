# -*- coding: utf-8 -*-

import json
import logging
from binascii import a2b_base64

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Avg
from django.http import HttpResponse
from django.shortcuts import redirect, render

from ..forms import BookHomeForm, AddCommentForm, ChangeRatingForm, StoreBookImageForm
from ..models import AddedBook, Book, BookRating, BookComment, TheUser
from ..recommend import get_recommend
from ..utils import html_escape, resize_image

BOOK_COVER_HEIGHT = 350
RANDOM_BOOKS_COUNT = 6

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
def selected_book(request, book_id):
    """
    Returns a page with selected book.

    :param django.core.handlers.wsgi.WSGIRequest request: The request for selecting book.
    :param int book_id: The identifier of a book.
    :return: A HTML page with selected book.
    """
    if request.user.is_authenticated():
        rel_objects = Book.get_related_objects_selected_book(request.user, book_id)
        user = TheUser.objects.get(id_user=request.user)

        recommend_books = get_recommend(request.user, AddedBook.get_user_added_books(request.user),
                                        RANDOM_BOOKS_COUNT, [book_id])
        book_rating = rel_objects['avg_book_rating']['rating__avg']
        book_rating_count = rel_objects['book_rating_count']

        context = {'book': rel_objects['book'],
                   'added_book': rel_objects['added_book'],
                   'added_book_count': AddedBook.get_count_added(book_id),
                   'comments': rel_objects['comments'],
                   'book_rating': book_rating if book_rating else '-',
                   'book_rating_count': '({})'.format(book_rating_count) if book_rating_count else '',
                   'estimation_count': range(1, 11),
                   'user': user,
                   'recommend_books': recommend_books}

        return render(request, 'selected_book.html', context)
    else:
        return redirect('index')


# ----------------------------------------------------------------------------------------------------------------------
def store_image(request):
    """
    Stores the book image to database.

    :param django.core.handlers.wsgi.WSGIRequest request:
    :return: The status of adding book.
    """
    if request.is_ajax():
        image_form = StoreBookImageForm(request.POST)

        if image_form.is_valid():
            with transaction.atomic():
                book = Book.objects.get(id=image_form.cleaned_data['id'])

                data = image_form.cleaned_data['image'].split(',')[1]
                bin_data = a2b_base64(data)
                book.photo.save('book_{}.png'.format(image_form.cleaned_data['id']), ContentFile(bin_data))

                logger.info("The image was stored for book with id: '{}'.".format(book.id))

                resize_image(book.photo.path, BOOK_COVER_HEIGHT)
                logger.info("Image '{}' successfully resized!".format(book.photo.path))

                return HttpResponse(json.dumps(True), content_type='application/json')
    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def add_book_to_home(request):
    """
    Adds book to list of user's added books.

    :param django.core.handlers.wsgi.WSGIRequest request: The request with id of a book.
    :return: The status of adding book.
    """
    if request.is_ajax():
        book_form = BookHomeForm(request.POST)

        if book_form.is_valid():
            user = TheUser.objects.get(id_user=request.user)
            book = Book.objects.get(id=book_form.cleaned_data['book'])

            AddedBook.objects.create(id_user=user, id_book=book)

            logger.info("User '{}' added book with id: '{}' to his own library."
                        .format(request.user, book_form.cleaned_data['book']))

            return HttpResponse(json.dumps({'book_id': book.id}), content_type='application/json')
    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def remove_book_from_home(request):
    """
    Removes book from list of user's added books.

    :param django.core.handlers.wsgi.WSGIRequest request: The request with id of a book.
    :return: The status of adding book.
    """
    if request.is_ajax():
        book_form = BookHomeForm(request.POST)

        if book_form.is_valid():
            AddedBook.objects.get(id_user=TheUser.objects.get(id_user=request.user),
                                  id_book=Book.objects.get(id=book_form.cleaned_data['book'])).delete()

            logger.info("User '{}' removed book with id: '{}' from his own library."
                        .format(request.user, book_form.cleaned_data['book']))

            return HttpResponse(json.dumps(True), content_type='application/json')
    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def change_rating(request):
    """
    Sets new rating to a book.

    :param django.core.handlers.wsgi.WSGIRequest request: The request with id of a book and new rating.
    :return: New average count of rating of a book.
    """
    if request.is_ajax():
        rating_form = ChangeRatingForm(request.POST)

        if rating_form.is_valid():
            with transaction.atomic():
                set_rating(request, rating_form)

                book_rating = BookRating.objects.filter(id_book=Book.objects.get(id=rating_form.cleaned_data['book']))

                data = {'avg_rating': round(book_rating.aggregate(Avg('rating'))['rating__avg'], 1),
                        'rating_count': '({})'.format(book_rating.count())}

                return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def set_rating(request, rating_form):
    """
    Changes rating of a book.

    :param django.core.handlers.wsgi.WSGIRequest request: The request for changing book rating.
    :param app.forms.ChangeRatingForm rating_form: The form with rating.
    """
    try:
        book_rating = BookRating.objects.get(id_user=TheUser.objects.get(id_user=request.user),
                                             id_book=Book.objects.get(id=rating_form.cleaned_data['book']))
        book_rating.rating = rating_form.cleaned_data['rating']
        book_rating.save()

    except ObjectDoesNotExist:
        BookRating.objects.create(id_user=TheUser.objects.get(id_user=request.user),
                                  id_book=Book.objects.get(id=rating_form.cleaned_data['book']),
                                  rating=rating_form.cleaned_data['rating'])

    finally:
        logger.info("User '{}' set rating '{}' to book with id: '{}'."
                    .format(request.user, rating_form.cleaned_data['rating'], rating_form.cleaned_data['book']))


# ----------------------------------------------------------------------------------------------------------------------
def add_comment(request):
    """
    Adds a comment.

    :param django.core.handlers.wsgi.WSGIRequest request: The request for adding a comment.
    :return: Response with successfully added comment.
    """
    if request.is_ajax():
        comment_form = AddCommentForm(request.POST)

        if comment_form.is_valid():
            comment = BookComment.objects.create(id_user=TheUser.objects.get(id_user=request.user),
                                                 id_book=Book.objects.get(id=comment_form.cleaned_data['book']),
                                                 text=comment_form.cleaned_data['comment'])

            user = TheUser.objects.get(id_user=request.user)
            user_photo = user.user_photo.url if user.user_photo else ''

            logger.info("User '{}' left comment with id: '{}' on book with id: '{}'."
                        .format(user, comment.id, comment.id_book.id))

            response_data = {
                'text': html_escape(comment.text),
                'username': request.user.username,
                'user_photo': user_photo,
                'posted_date': comment.posted_date.strftime('%d-%m-%Y')
            }
            return HttpResponse(json.dumps(response_data), content_type='application/json')
    else:
        return HttpResponse(status=404)
