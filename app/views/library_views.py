# -*- coding: utf-8 -*-

import json
from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from ..forms import SortForm, SearchBookForm, BookPagingForm
from ..models import Category, Book, Author
from ..views import process_method, process_ajax, process_form

MOST_READ_BOOKS_COUNT = 9


# ----------------------------------------------------------------------------------------------------------------------
@process_method('GET', 404)
def all_categories(request):
    """
    Returns page with book categories.
    """
    categories = Category.objects.all().order_by('category_name')
    most_readable_books = Book.sort_by_readable(request.user, count=MOST_READ_BOOKS_COUNT)
    books_count = Book.objects.all().count()

    return render(request, 'categories.html', {'categories': categories,
                                               'most_readable_books': most_readable_books[:9],
                                               'books_count': books_count})


# ----------------------------------------------------------------------------------------------------------------------
@process_method('GET', 404)
def selected_category(request, category_id):
    """
    Returns page with selected category.
    """
    category = get_object_or_404(Category, id=category_id)
    books = Book.objects.filter(id_category=category).order_by('book_name')
    filtered_books = Book.exclude_private_books(request.user, books)

    paginator = Paginator(filtered_books, settings.BOOKS_PER_PAGE)
    page = paginator.page(1)

    context = {
        'category': category,
        'books': page.object_list,
        'total_books_count': books.count(),
        'has_next': page.has_next()
    }
    return render(request, 'selected_category.html', context)


# ----------------------------------------------------------------------------------------------------------------------
@process_method('GET', 404)
def selected_author(request, author_id):
    """
    Returns a page with a list of books of a selected author.
    """
    author = get_object_or_404(Author, id=author_id)
    books = Book.objects.filter(id_author=author).order_by('book_name')

    filtered_books = Book.exclude_private_books(request.user, books)

    context = {'author': author, 'books': filtered_books}
    return render(request, 'selected_author.html', context)


# ----------------------------------------------------------------------------------------------------------------------
@process_ajax(404)
@process_form('GET', SortForm, 400)
def sort(request, form):
    """
    Returns data sorted data depending on criterion.
    """
    criterion_dict = {'book_name': Book.sort_by_book_name,
                      'author': Book.sort_by_author,
                      'estimation': Book.sort_by_estimation}

    category = Category.objects.get(id=form.cleaned_data['category'])
    books_count = Book.objects.filter(id_category=category).count()

    if form.cleaned_data['criterion'] == 'most_readable':
        books = Book.sort_by_readable(request.user, category, books_count)
    else:
        books = criterion_dict[form.cleaned_data['criterion']](request.user, category)

    paginator = Paginator(books, settings.BOOKS_PER_PAGE)
    page = paginator.page(form.cleaned_data['page'])

    context = {
        'category': category.id,
        'criterion': form.cleaned_data['criterion'],
        'books': page.object_list,
        'has_next': page.has_next(),
        'next_page': page.next_page_number() if page.has_next() else paginator.num_pages
    }

    return HttpResponse(json.dumps(context), content_type='application/json')


# ----------------------------------------------------------------------------------------------------------------------
@process_ajax(404)
@process_form('GET', SearchBookForm, 400)
def find_books(request, form):
    """
    Generates list with books of data which user entered. At first it check full equality in name,
    after tries to check if contains some part of entered data.
    """
    search_data = form.cleaned_data['data']
    filtered_books = Book.exclude_private_books(request.user, Book.fetch_books(search_data))

    paginator = Paginator(filtered_books, settings.BOOKS_PER_PAGE)
    page = paginator.page(form.cleaned_data['page'])

    response = {
        'books': Book.generate_books(page.object_list),
        'has_next': page.has_next(),
        'next_page': page.next_page_number() if page.has_next() else paginator.num_pages
    }
    return HttpResponse(json.dumps(response), content_type='application/json')


# ----------------------------------------------------------------------------------------------------------------------
@process_ajax(404)
@process_form('GET', BookPagingForm, 400)
def load_books(request, category_id, form):
    """
    Ajax request handler for outputting books page by page.
    """
    category = get_object_or_404(Category, id=category_id)
    books = Book.objects.filter(id_category=category).order_by('book_name')
    filtered_books = Book.exclude_private_books(request.user, books)

    paginator = Paginator(filtered_books, settings.BOOKS_PER_PAGE)
    page = paginator.page(form.cleaned_data['page'])

    response = {
        'category_id': category_id,
        'books': Book.generate_books(page.object_list),
        'has_next': page.has_next(),
        'next_page': page.next_page_number() if page.has_next() else paginator.num_pages
    }
    return HttpResponse(json.dumps(response), content_type='application/json')
