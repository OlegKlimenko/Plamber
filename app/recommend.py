# -*- coding: utf-8 -*-

import random

from .models import Book

START_RECOMMEND = 10


# ----------------------------------------------------------------------------------------------------------------------
def get_recommend(user, books, result_count):
    """
    Return the recommend books.

    :param django.contrib.auth.models.User                    user:         The request user.
    :param django.db.models.query.QuerySet[.models.AddedBook] books:        The user's added book list.
    :param int                                                result_count: The count of random generated books.

    :return set[.models.Book]: The recommend books.
    """
    added_books = get_by_added(books, result_count)

    return added_books


# ----------------------------------------------------------------------------------------------------------------------
def get_by_added(added_books, result_count):
    """
    If added books is present, return random books from the most read by user category.
    Otherwise return random books from all categories.

    :param django.db.models.query.QuerySet[.models.AddedBook] added_books:  The user's added book list.
    :param int                                                result_count: The count of random generated books.

    :return set[.models.Book]: The random generated books.
    """
    if added_books:
        books_categories = list(added_books.values_list('id_book__id_category', flat=True))
        added_books_ids = list(added_books.values_list('id_book', flat=True))

        most_read_category = max(set(books_categories), key=books_categories.count)
        category_books = Book.objects.filter(id_category=most_read_category).exclude(id__in=added_books_ids)

        return unique_books(category_books, result_count)

    else:
        return unique_books(Book.objects.all(), result_count)


# ----------------------------------------------------------------------------------------------------------------------
def unique_books(books, result_count):
    """
    Return unique random books from given list of books.

    :param django.db.models.query.QuerySet[.models.Book] books:        The given list of books.
    :param int                                           result_count: The count of unique books.

    :return set[.models.Book]: The unique books.
    """
    unique = set()

    if books.count() > START_RECOMMEND:
        while len(unique) < result_count:
            unique.add(books[random.randint(0, books.count() - 1)])

    return unique
