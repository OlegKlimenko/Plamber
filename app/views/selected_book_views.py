# -*- coding: utf-8 -*-

import json
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import RequestContext, loader

from app.forms import BookHomeForm, AddCommentForm, ChangeRatingForm
from app.models import AddedBook, Book, BookRating, BookComment, TheUser


# ----------------------------------------------------------------------------------------------------------------------
def selected_book_view(request, book_id):
    """
    Returns a page with selected book.

    :param django.core.handlers.wsgi.WSGIRequest request: The request for selecting book.
    :return: A HTML page with selected book.
    """
    if request.user.is_authenticated():
        rel_objects = get_related_objects(request, book_id)

        template = loader.get_template('selected_book.html')
        context = RequestContext(request, {'book': rel_objects['book'],
                                           'added_book': rel_objects['added_book'],
                                           'comments': rel_objects['comments'],
                                           'book_rating': rel_objects['avg_book_rating']['rating__avg']})
        return HttpResponse(template.render(context))
    else:
        return redirect('index')


# ----------------------------------------------------------------------------------------------------------------------
def get_related_objects(request, book_id):
    """
    Returns the related objects of selected book

    :param django.core.handlers.wsgi.WSGIRequest request: The request for selecting book.
    :param int book_id: The ID of selected book.
    :return: Related objects.
    """
    book = Book.objects.get(id=book_id)
    avg_book_rating = BookRating.objects.filter(id_book=book).aggregate(Avg('rating'))

    try:
        added_book = AddedBook.objects.get(id_user=TheUser.objects.get(id_user=request.user), id_book=book)
    except ObjectDoesNotExist:
        added_book = None

    try:
        comments = BookComment.objects.filter(id_book=Book.objects.get(id=book_id)).order_by('-id')
    except ObjectDoesNotExist:
        comments = None

    return {'book': book, 'avg_book_rating': avg_book_rating, 'added_book': added_book, 'comments': comments}


# ----------------------------------------------------------------------------------------------------------------------
def add_book_to_home_view(request):
    """
    Adds book to list of user's added books.

    :param django.core.handlers.wsgi.WSGIRequest request: The request with id of a book.
    :return: The status of adding book.
    """
    if request.is_ajax():
        book_form = BookHomeForm(request.POST)

        if book_form.is_valid():
            AddedBook.objects.create(id_user=TheUser.objects.get(id_user=request.user),
                                     id_book=Book.objects.get(id=book_form.cleaned_data['book_id']))
            return HttpResponse(json.dumps(True), content_type='application/json')
    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def remove_book_from_home_view(request):
    """
    Removes book from list of user's added books.

    :param django.core.handlers.wsgi.WSGIRequest request: The request with id of a book.
    :return: The status of adding book.
    """
    if request.is_ajax():
        book_form = BookHomeForm(request.POST)

        if book_form.is_valid():
            AddedBook.objects.get(id_user=TheUser.objects.get(id_user=request.user),
                                  id_book=Book.objects.get(id=book_form.cleaned_data['book_id'])).delete()
            return HttpResponse(json.dumps(True), content_type='application/json')
    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def change_rating_view(request):
    """
    Sets new rating to a book.

    :param django.core.handlers.wsgi.WSGIRequest request: The request with id of a book and new rating.
    :return: New average count of rating of a book.
    """
    if request.is_ajax():
        rating_form = ChangeRatingForm(request.POST)

        if rating_form.is_valid():
            change_rating(request, rating_form)

            avg_book_rating = BookRating.objects.filter(
                id_book=Book.objects.get(id=rating_form.cleaned_data['book_id'])).aggregate(Avg('rating'))

            return HttpResponse(json.dumps(avg_book_rating['rating__avg']), content_type='application/json')
    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def change_rating(request, rating_form):
    """
    Changes rating of a book.

    :param django.core.handlers.wsgi.WSGIRequest request: The request for changing book rating.
    :param app.forms.ChangeRatingForm rating_form: The form with rating.
    """
    try:
        book_rating = BookRating.objects.get(id_user=TheUser.objects.get(id_user=request.user),
                                             id_book=Book.objects.get(id=rating_form.cleaned_data['book_id']))
        book_rating.rating = rating_form.cleaned_data['rating']
        book_rating.save()

    except ObjectDoesNotExist:
        BookRating.objects.create(id_user=TheUser.objects.get(id_user=request.user),
                                  id_book=Book.objects.get(id=rating_form.cleaned_data['book_id']),
                                  rating=rating_form.cleaned_data['rating'])


# ----------------------------------------------------------------------------------------------------------------------
def add_comment_view(request):
    """
    Adds a comment.

    :param django.core.handlers.wsgi.WSGIRequest request: The request for adding a comment.
    :return: Response with successfully added comment.
    """
    if request.is_ajax():
        comment_form = AddCommentForm(request.POST)

        if comment_form.is_valid():
            BookComment.objects.create(id_user=TheUser.objects.get(id_user=request.user),
                                       id_book=Book.objects.get(id=comment_form.cleaned_data['book_id']),
                                       text=comment_form.cleaned_data['comment'])
            return HttpResponse(json.dumps(request.user.username), content_type='application/json')
    else:
        return HttpResponse(status=404)
