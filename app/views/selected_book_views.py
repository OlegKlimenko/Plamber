# -*- coding: utf-8 -*-

import json
import logging
from binascii import a2b_base64

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Avg
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.html import escape

from ..forms import BookHomeForm, AddCommentForm, ChangeRatingForm, StoreBookImageForm, LoadCommentsForm, ReportForm
from ..models import AddedBook, Book, BookRating, BookComment, TheUser, SupportMessage
from ..recommend import get_recommend
from ..utils import resize_image
from ..views import process_method, process_ajax, process_form

BOOK_COVER_HEIGHT = 350
COMMENTS_PER_PAGE = 20
COMMENTS_START_PAGE = 1
RANDOM_BOOKS_COUNT = 6

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
def selected_book(request, book_id):
    """
    Returns a page with selected book.
    """
    get_object_or_404(Book, id=book_id)
    rel_objects = Book.get_related_objects_selected_book(request.user, book_id)

    user_rated = None

    if not request.user.is_anonymous:
        user = TheUser.objects.get(id_user=request.user)
        user_rated = BookRating.objects.filter(id_book__id=book_id, id_user=user)
    else:
        user = request.user

    if rel_objects['book'].private_book and rel_objects['book'].who_added != user:
        return HttpResponse(status=404)

    recommend_books = get_recommend(
        request.user, AddedBook.get_user_added_books(request.user), RANDOM_BOOKS_COUNT, [book_id]
    )
    book_rating = rel_objects['avg_book_rating']['rating__avg']
    book_rating_count = rel_objects['book_rating_count']

    comments = rel_objects['comments']
    comments_paginator = Paginator(comments, COMMENTS_PER_PAGE)
    page = comments_paginator.page(COMMENTS_START_PAGE)

    context = {
        'book': rel_objects['book'],
        'added_book': rel_objects['added_book'],
        'added_book_count': AddedBook.get_count_added(book_id),
        'comments': page.object_list,
        'comments_page': COMMENTS_START_PAGE,
        'comments_has_next_page': page.has_next(),
        'book_rating': book_rating if book_rating else '-',
        'book_rating_count': '({})'.format(book_rating_count) if book_rating_count else '',
        'estimation_count': range(1, 11),
        'user': user,
        'recommend_books': recommend_books,
        'user_rated': user_rated[0] if user_rated else None,
        'report_form': ReportForm()
    }

    return render(request, 'selected_book.html', context)


# ----------------------------------------------------------------------------------------------------------------------
@process_ajax(404)
@process_form('POST', StoreBookImageForm, 400)
def store_image(request, form):
    """
    Stores the book image to database.
    """
    with transaction.atomic():
        book = Book.objects.get(id=form.cleaned_data['id'])

        data = form.cleaned_data['image'].split(',')[1]
        bin_data = a2b_base64(data)
        book.photo.save('book_{}.png'.format(form.cleaned_data['id']), ContentFile(bin_data))

        logger.info("The image was stored for book with id: '{}'.".format(book.id))

        resize_image(book.photo.path, BOOK_COVER_HEIGHT)
        logger.info("Image '{}' successfully resized!".format(book.photo.path))

        return HttpResponse(json.dumps(True), content_type='application/json')


# ----------------------------------------------------------------------------------------------------------------------
@process_ajax(404)
@process_form('POST', BookHomeForm, 400)
def add_book_to_home(request, form):
    """
    Adds book to list of user's added books.
    """
    user = TheUser.objects.get(id_user=request.user)
    book = Book.objects.get(id=form.cleaned_data['book'])

    if book.private_book and book.who_added != user:
        return HttpResponse(status=404)

    if book.blocked_book:
        return HttpResponse(status=400)

    if AddedBook.objects.filter(id_user=user, id_book=book).exists():
        return HttpResponse(status=404)

    AddedBook.objects.create(id_user=user, id_book=book)

    logger.info("User '{}' added book with id: '{}' to his own library."
                .format(request.user, form.cleaned_data['book']))

    return HttpResponse(json.dumps({'book_id': book.id}), content_type='application/json')


# ----------------------------------------------------------------------------------------------------------------------
@process_ajax(404)
@process_form('POST', BookHomeForm, 400)
def remove_book_from_home(request, form):
    """
    Removes book from list of user's added books.
    """
    book = get_object_or_404(Book, id=form.cleaned_data['book'])

    get_object_or_404(AddedBook, id_user=TheUser.objects.get(id_user=request.user), id_book=book).delete()
    logger.info("User '{}' removed book with id: '{}' from his own library."
                .format(request.user, form.cleaned_data['book']))

    if book.blocked_book:
        return HttpResponse(json.dumps(False), content_type='application/json')

    return HttpResponse(json.dumps(True), content_type='application/json')


# ----------------------------------------------------------------------------------------------------------------------
@process_ajax(404)
@process_form('POST', ChangeRatingForm, 400)
def change_rating(request, form):
    with transaction.atomic():
        set_rating(request, form)

        book_rating = BookRating.objects.filter(id_book=Book.objects.get(id=form.cleaned_data['book']))

        data = {'avg_rating': round(book_rating.aggregate(Avg('rating'))['rating__avg'], 1),
                'rating_count': '({})'.format(book_rating.count())}

        return HttpResponse(json.dumps(data), content_type='application/json')


# ----------------------------------------------------------------------------------------------------------------------
def set_rating(request, rating_form):
    """
    Checks if rating for books exists. If exists, changes it. If not, creates a new one.
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
@process_ajax(404)
@process_form('POST', AddCommentForm, 400)
def add_comment(request, form):
    comment = BookComment.objects.create(id_user=TheUser.objects.get(id_user=request.user),
                                         id_book=Book.objects.get(id=form.cleaned_data['book']),
                                         text=form.cleaned_data['comment'])

    user = get_object_or_404(TheUser, id_user=request.user)
    user_photo = user.user_photo.url if user.user_photo else ''

    logger.info("User '{}' left comment with id: '{}' on book with id: '{}'."
                .format(user, comment.id, comment.id_book.id))

    response_data = {
        'username': escape(request.user.username),
        'user_photo': user_photo,
        'posted_date': comment.posted_date.strftime('%d-%m-%Y'),
        'text': escape(comment.text)
    }
    return HttpResponse(json.dumps(response_data), content_type='application/json')


# ----------------------------------------------------------------------------------------------------------------------
@process_ajax(404)
@process_form('POST', LoadCommentsForm, 400)
def load_comments(request, form):
    book = Book.objects.get(id=form.cleaned_data['book_id'])
    comments = BookComment.objects.filter(id_book=book).order_by('-id')
    next_page_num = form.cleaned_data['page'] + 1

    comments_paginator = Paginator(comments, COMMENTS_PER_PAGE)
    page = comments_paginator.page(next_page_num)

    json_comments = [{
        'username': escape(comment.id_user.id_user.username),
        'user_photo': comment.id_user.user_photo.url if comment.id_user.user_photo else '',
        'posted_date': comment.posted_date.strftime('%d-%m-%Y'),
        'text': escape(comment.text)
    } for comment in page.object_list]

    response_data = {
        'comments': json_comments,
        'current_page': next_page_num,
        'has_next_page': page.has_next(),
        'book_id': book.id
    }

    return HttpResponse(json.dumps(response_data), content_type='application/json')


# ----------------------------------------------------------------------------------------------------------------------
@process_method('POST', 400)
@process_form('POST', ReportForm, 400)
def report_book(request, form):
    """
    Creates a report of incorrect entered data.
    """
    SupportMessage.objects.create(
        email=request.user.email,
        text=form.cleaned_data['text']
    )
    return HttpResponse(status=200)
