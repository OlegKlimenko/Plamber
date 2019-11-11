# -*- coding: utf-8 -*-

import json
from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.html import escape

from ..forms import SortForm, SearchBookForm, BookPagingForm
from ..models import Category, Book, Author

MOST_READ_BOOKS_COUNT = 9


# ----------------------------------------------------------------------------------------------------------------------
def all_categories(request):
    """
    Returns page with book categories.
    """
    if request.method == "GET":
        categories = Category.objects.all().order_by('category_name')
        most_readable_books = Book.sort_by_readable(request.user, count=MOST_READ_BOOKS_COUNT)
        books_count = Book.objects.all().count()

        return render(request, 'categories.html', {'categories': categories,
                                                   'most_readable_books': most_readable_books[:9],
                                                   'books_count': books_count})
    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def selected_category(request, category_id):
    """
    Returns page with selected category.
    """
    if request.method == 'GET':
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

    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def selected_author(request, author_id):
    """
    Returns a page with a list of books of a selected author.
    """
    if request.method == 'GET':
        author = get_object_or_404(Author, id=author_id)
        books = Book.objects.filter(id_author=author).order_by('book_name')

        filtered_books = Book.exclude_private_books(request.user, books)

        context = {'author': author, 'books': filtered_books}
        return render(request, 'selected_author.html', context)

    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def sort(request):
    """
    Returns data sorted data depending on criterion.
    """
    if request.is_ajax():
        sort_form = SortForm(request.GET)

        if sort_form.is_valid():
            criterion_dict = {'book_name': Book.sort_by_book_name,
                              'author': Book.sort_by_author,
                              'estimation': Book.sort_by_estimation}

            category = Category.objects.get(id=sort_form.cleaned_data['category'])
            books_count = Book.objects.filter(id_category=category).count()

            if sort_form.cleaned_data['criterion'] == 'most_readable':
                books = Book.sort_by_readable(request.user, category, books_count)
            else:
                books = criterion_dict[sort_form.cleaned_data['criterion']](request.user, category)

            for book in books:
                book['name'] = escape(book['name'])
                book['author'] = escape(book['author'])

            paginator = Paginator(books, settings.BOOKS_PER_PAGE)
            page = paginator.page(sort_form.cleaned_data['page'])

            context = {
                'category': category.id,
                'criterion': sort_form.cleaned_data['criterion'],
                'books': page.object_list,
                'has_next': page.has_next(),
                'next_page': page.next_page_number() if page.has_next() else paginator.num_pages
            }

            return HttpResponse(json.dumps(context), content_type='application/json')
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def find_books(request):
    """
    Generates list with books of data which user entered. At first it check full equality in name,
    after tries to check if contains some part of entered data.
    """
    if request.is_ajax():
        search_book_form = SearchBookForm(request.GET)

        if search_book_form.is_valid():
            search_data = search_book_form.cleaned_data['data']
            filtered_books = Book.exclude_private_books(request.user, Book.fetch_books(search_data))

            paginator = Paginator(filtered_books, settings.BOOKS_PER_PAGE)
            page = paginator.page(search_book_form.cleaned_data['page'])

            books = Book.generate_books(page.object_list)
            for book in books:
                book['name'] = escape(book['name'])
                book['author'] = escape(book['author'])

            response = {
                'books': books,
                'has_next': page.has_next(),
                'next_page': page.next_page_number() if page.has_next() else paginator.num_pages
            }
            return HttpResponse(json.dumps(response), content_type='application/json')
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def load_books(request, category_id):
    """
    Ajax request handler for outputting books page by page.
    """
    if request.is_ajax():
        form = BookPagingForm(request.GET)

        if form.is_valid():
            category = get_object_or_404(Category, id=category_id)
            books = Book.objects.filter(id_category=category).order_by('book_name')
            filtered_books = Book.exclude_private_books(request.user, books)

            paginator = Paginator(filtered_books, settings.BOOKS_PER_PAGE)
            page = paginator.page(form.cleaned_data['page'])

            books = Book.generate_books(page.object_list)
            for book in books:
                book['name'] = escape(book['name'])
                book['author'] = escape(book['author'])

            response = {
                'category_id': category_id,
                'books': books,
                'has_next': page.has_next(),
                'next_page': page.next_page_number() if page.has_next() else paginator.num_pages
            }
            return HttpResponse(json.dumps(response), content_type='application/json')

        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=404)
