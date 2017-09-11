# -*- coding: utf-8 -*-

import logging

from django.db import models
from django.db.models import Avg, Count
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse
from django.utils.html import escape

from .storage import OverwriteStorage

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
class TheUser(models.Model):
    """
    Class for user objects in database.
    """
    id_user = models.OneToOneField(User)
    user_photo = models.ImageField(blank=True, upload_to='user', storage=OverwriteStorage())
    auth_token = models.CharField(max_length=50, null=True, blank=True)

    # ------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        return str(self.id_user)


# ----------------------------------------------------------------------------------------------------------------------
class Category(models.Model):
    """
    Class for category objects in database.
    """
    category_name = models.CharField(max_length=30)

    # ------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        return self.category_name


# ----------------------------------------------------------------------------------------------------------------------
class Author(models.Model):
    """
    Class for author objects in database.
    """
    author_name = models.CharField(max_length=100)

    # ------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        return self.author_name

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_authors_list(author_part):
        """
        Returns a list of authors.

        :param str author_part: The part of author name
        :return list[str]:
        """
        return list(
            Author.objects.filter(author_name__icontains=author_part)[:10].values_list('author_name', flat=True)
        )


# ----------------------------------------------------------------------------------------------------------------------
class Language(models.Model):
    """
    Class for language objects in database.
    """
    language = models.CharField(max_length=30)

    # ------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        return self.language


# ----------------------------------------------------------------------------------------------------------------------
class Book(models.Model):
    """
    Class for book objects in database.
    """
    book_name = models.CharField(max_length=150)
    id_author = models.ForeignKey(Author)
    id_category = models.ForeignKey(Category)
    description = models.CharField(max_length=1000, blank=True)
    language = models.ForeignKey(Language)
    photo = models.ImageField(blank=True, upload_to='book_cover')
    book_file = models.FileField(upload_to='book_file')
    who_added = models.ForeignKey(TheUser)
    upload_date = models.DateTimeField(auto_now=True)
    private_book = models.BooleanField(default=False)

    # ------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        return "{0}, {1}, язык({2})".format(self.book_name, self.id_author, self.language)

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_related_objects_for_create(user_id, book_form):
        """
        Selects related objects to book instance when create new book; creates author object if needed.

        :param int user_id: The id of user.
        :param app.forms.AddBookForm book_form: The form with received data.
        :return: A dict of objects related to book.
        """
        try:
            author = Author.objects.get(author_name__iexact=book_form.cleaned_data['author'])
        except ObjectDoesNotExist:
            author = Author.objects.create(author_name=book_form.cleaned_data['author'])

            logger.info("Created new author with name: '{}' and id: '{}'."
                        .format(author.author_name, author.id))

        category = Category.objects.get(category_name=book_form.cleaned_data['category'])
        lang = Language.objects.get(language=book_form.cleaned_data['language'])
        user = TheUser.objects.get(id_user=user_id)

        return {'author': author, 'category': category, 'lang': lang, 'user': user}

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_related_objects_selected_book(user, book_id):
        """
        Returns the related objects of selected book

        :param app.models.TheUser user: The request for selecting book.
        :param int book_id: The ID of selected book.
        :return: Related objects.
        """
        book = Book.objects.get(id=book_id)
        book_rating = BookRating.objects.filter(id_book=book)

        try:
            added_book = AddedBook.objects.get(id_user=TheUser.objects.get(id_user=user), id_book=book)
        except ObjectDoesNotExist:
            added_book = None

        comments = BookComment.objects.filter(id_book=Book.objects.get(id=book_id)).order_by('-id')

        return {'book': book,
                'avg_book_rating': book_rating.aggregate(Avg('rating')),
                'book_rating_count': book_rating.count(),
                'added_book': added_book,
                'comments': comments}

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def sort_by_book_name(user, category):
        """
        Sorts books by book name.

        :param django.contrib.auth.models.User  user:     The request user.
        :param app.models.Category              category: The category.

        :return list[dict[str, str]]: list of books with data.
        """
        books = Book.objects.filter(id_category=category).order_by('book_name')
        filtered_books = Book.exclude_private_books(user, books)

        return Book.generate_books(filtered_books)

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def sort_by_author(user, category):
        """
        Sorts books by author.

        :param django.contrib.auth.models.User  user:     The request user.
        :param app.models.Category              category: The category.

        :return list[dict[str, str]]: list of books with data.
        """
        books = Book.objects.filter(id_category=category).order_by('id_author__author_name')
        filtered_books = Book.exclude_private_books(user, books)

        return Book.generate_books(filtered_books)

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def sort_by_estimation(user, category):
        """
        Sorts books by average count of estimation of each book. Uses aggregate function.

        :param django.contrib.auth.models.User  user:     The request user.
        :param app.models.Category              category: The category.

        :return: The list with sorted books.
        """
        books = []
        filtered_books = Book.exclude_private_books(user, Book.objects.filter(id_category=category))

        for item in filtered_books:
            book_rating = BookRating.objects.filter(id_book=item).aggregate(Avg('rating'))
            book = {'id': item.id,
                    'name': item.book_name,
                    'author': item.id_author.author_name,
                    'url': item.photo.url if item.photo else '',
                    'rating': book_rating['rating__avg']}
            books.append(book)

        return sorted(books, key=lambda info: (info['rating'] is not None, info['rating']), reverse=True)

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def sort_by_readable(user, category):
        """

        Sorts books by most readable criterion. Uses aggregate 'count' function.

        :param django.contrib.auth.models.User  user:     The request user.
        :param app.models.Category              category: The category.

        :return: The list with sorted books.
        """
        books = []
        filtered_books = Book.exclude_private_books(user, Book.objects.filter(id_category=category))

        for item in filtered_books:
            book_read_count = AddedBook.objects.filter(id_book=item).aggregate(Count('id_user'))
            book = {'id': item.id,
                    'name': item.book_name,
                    'author': item.id_author.author_name,
                    'url': item.photo.url if item.photo else '',
                    'read_count': book_read_count['id_user__count']}
            books.append(book)

        return sorted(books, key=lambda info: info['read_count'], reverse=True)

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def generate_books(filtered_books):
        """
        Generates list with books for specific data and special criterion.

        :param list filtered_books: The list of books after fetching them from database.
        :return list[dict[str, str]]: list of books with data.
        """
        books = [
            {'id': item.id,
             'name': item.book_name,
             'author': item.id_author.author_name,
             'url': item.photo.url if item.photo else ''} for item in filtered_books
        ]

        return books

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def fetch_books(search_data):
        """
        Generates list of books, fetched by different criterion depending on 'search_data' argument.

        :param str search_data: The string with data by which create search books.
        :return: The generated list of books.
        """
        filtered_books = list(Book.objects.filter(book_name=search_data))
        filtered_books += list(Book.objects.filter(book_name__icontains=search_data))
        filtered_books += list(Book.objects.filter(id_author__author_name=search_data))
        filtered_books += list(Book.objects.filter(id_author__author_name__icontains=search_data))

        return list(set(filtered_books))

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def generate_existing_books(book_part):
        """
        Returns a list of books.

        :param str book_part: Criterion for returning books.
        :return:
        """
        return [{'url': reverse('book', args=[escape(item[0])]), 'name': escape(item[1])} for item in
                Book.objects.filter(book_name__icontains=book_part)[:10].values_list('id', 'book_name')]

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def exclude_private_books(user, books):
        """
        Returns the list of books without private books which not depend to current user

        :param django.contrib.auth.models.User               user:         The request user.
        :param django.db.models.query.QuerySet[.models.Book] books:        The given list of books.

        :return list[.models.Book]: List of books.
        """
        the_user = TheUser.objects.get(id_user=user)
        filtered_books = []

        for book in books:
            if book.private_book and book.who_added != the_user:
                continue

            filtered_books.append(book)

        return filtered_books


# ----------------------------------------------------------------------------------------------------------------------
class BookRating(models.Model):
    """
    Class for book rating objects in database.
    """
    id_user = models.ForeignKey(TheUser)
    id_book = models.ForeignKey(Book)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])


# ----------------------------------------------------------------------------------------------------------------------
class BookComment(models.Model):
    """
    Class for book comment objects in database.
    """
    id_user = models.ForeignKey(TheUser)
    id_book = models.ForeignKey(Book)
    text = models.CharField(max_length=500)
    posted_date = models.DateField(auto_now=True)


# ----------------------------------------------------------------------------------------------------------------------
class AddedBook(models.Model):
    """
    Class for added book objects in database.
    """
    id_user = models.ForeignKey(TheUser)
    id_book = models.ForeignKey(Book)
    last_page = models.PositiveIntegerField(default=1)
    last_read = models.DateTimeField(auto_now=True)

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_user_added_books(user):
        """
        Returns the list of books which user added in his home library

        :param app.models.TheUser user: The user instance.
        :return list[app.models.Book]:
        """
        return AddedBook.objects.filter(id_user=TheUser.objects.get(id_user=user)).order_by('-last_read')

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_count_added(book_id):
        """
        Returns the added count of selected book.

        :param int book_id: The id of book which we are counting.
        :return int: The count of added books
        """
        return AddedBook.objects.filter(id_book__id=book_id).count()


# ----------------------------------------------------------------------------------------------------------------------
class Post(models.Model):
    """
    Class for posts in blog about project.
    """
    heading = models.CharField(max_length=140)
    user = models.ForeignKey(TheUser)
    posted_date = models.DateField(auto_now=True)
    text = models.TextField()
