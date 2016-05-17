# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import RequestContext, loader
from django.core.exceptions import ObjectDoesNotExist

from app.forms import GenerateAuthorsForm, AddBookForm
from app.models import Author, Book, Category, Language, TheUser


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

            template = loader.get_template('add_book.html')
            context = RequestContext(request, {'categories': categories, 'languages': languages})
            return HttpResponse(template.render(context))
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
            list_of_authors = Author.objects.filter(
                author_name__icontains=authors_form.cleaned_data['author_part'])[:10]
            list_of_authors = list(list_of_authors.values_list('author_name', flat=True))

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
            rel_objects = get_related_objects(request.user.id, book_form)

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


# ----------------------------------------------------------------------------------------------------------------------
def get_related_objects(user_id, book_form):
    """
    Selects objects related to book instance; creates author object if needed.

    :param int user_id: The id of user.
    :param app.forms.AddBookForm book_form: The form with received data.
    :return: A dict of objects related to book.
    """
    try:
        author = Author.objects.get(author_name__iexact=book_form.cleaned_data['author'])
    except ObjectDoesNotExist:
        author = Author.objects.create(author_name=book_form.cleaned_data['author'])

    # --- @ todo method for getting image in book object
    category = Category.objects.get(category_name=book_form.cleaned_data['category'])
    lang = Language.objects.get(language=book_form.cleaned_data['language'])
    user = TheUser.objects.get(id_user=user_id)

    return {'author': author, 'category': category, 'lang': lang, 'user': user}
