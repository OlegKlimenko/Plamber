# -*- coding: utf-8 -*-

import json
import os

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from django.test import TestCase, Client, override_settings

from ...models import Author, Book, AddedBook, Category, Language, TheUser, BookRating
from ...views.library_views import all_categories, selected_category, selected_author, sort, find_books, load_books

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(TEST_DIR, '../fixtures')

NOT_EXISTS_CATEGORY = 10000

# ----------------------------------------------------------------------------------------------------------------------
@override_settings(BOOKS_PER_PAGE=2)
class LibraryViewsTestCase(TestCase):

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def setUpTestData(cls):
        test_book_path = os.path.join(TEST_DATA_DIR, 'test_book.pdf')

        cls.xhr = 'XMLHttpRequest'
        cls.user = User.objects.create_user(username='libusername', email='lib@user.com', password='password')
        cls.the_user = TheUser.objects.get(id_user=cls.user)

        cls.anonymous_client = Client()
        cls.logged_client = Client()
        cls.logged_client.login(username='libusername', password='password')

        cls.category = Category.objects.create(category_name='CustomCategoryName')
        cls.language = Language.objects.create(language='French')
        cls.author1 = Author.objects.create(author_name='SomeAuthorCategoryName')
        cls.author2 = Author.objects.create(author_name='SomeOtherCategoryNameAuthor')

        cls.book1 = Book.objects.create(
            book_name='category_book_test1',
            id_author=cls.author1,
            id_category=cls.category,
            language=cls.language,
            book_file=SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
            who_added=cls.the_user
        )
        cls.book2 = Book.objects.create(
            book_name='category_book_test2',
            id_author=cls.author2,
            id_category=cls.category,
            language=cls.language,
            book_file=SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
            who_added=cls.the_user
        )
        cls.book3 = Book.objects.create(
            book_name='category_book_test3',
            id_author=cls.author2,
            id_category=cls.category,
            language=cls.language,
            book_file=SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
            who_added=cls.the_user
        )

        AddedBook.objects.create(id_user=cls.the_user, id_book=cls.book1)
        AddedBook.objects.create(id_user=cls.the_user, id_book=cls.book2)

        BookRating.objects.create(id_user=cls.the_user, id_book=cls.book3, rating=10)
        BookRating.objects.create(id_user=cls.the_user, id_book=cls.book2, rating=7)
        BookRating.objects.create(id_user=cls.the_user, id_book=cls.book1, rating=5)

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def tearDownClass(cls):
        for book in Book.objects.all():
            if os.path.exists(book.book_file.path):
                os.remove(book.book_file.path)
            if book.photo and os.path.exists(book.photo.path):
                os.remove(book.photo.path)

    # ------------------------------------------------------------------------------------------------------------------
    def test_all_categories_invalid_request_method(self):
        response = self.anonymous_client.post(reverse('categories'))

        self.assertEqual(response.resolver_match.func, all_categories)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_all_categories(self):
        response = self.anonymous_client.get(reverse('categories'))

        self.assertEqual(response.resolver_match.func, all_categories)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'categories.html')
        self.assertIn('categories', response.context)
        self.assertIn('most_readable_books', response.context)
        self.assertIn('books_count', response.context)
        self.assertEqual(len(response.context['categories']), Category.objects.all().count())
        # TODO: Add test to most readable books
        self.assertEqual(response.context['books_count'], Book.objects.all().count())

    # ------------------------------------------------------------------------------------------------------------------
    def test_selected_category_invalid_request_method(self):
        response = self.anonymous_client.post(reverse('category', kwargs={'category_id': 10000}))

        self.assertEqual(response.resolver_match.func, selected_category)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_selected_category_not_exists(self):
        response = self.anonymous_client.get(reverse('category', kwargs={'category_id': 10000}))

        self.assertEqual(response.resolver_match.func, selected_category)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_selected_category_success(self):
        response = self.anonymous_client.get(reverse('category', kwargs={'category_id': self.category.id}))

        self.assertEqual(response.resolver_match.func, selected_category)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'selected_category.html')
        self.assertIn('category', response.context)
        self.assertIn('books', response.context)
        self.assertIn('total_books_count', response.context)
        self.assertIn('has_next', response.context)
        self.assertEqual(response.context['category'].category_name, 'CustomCategoryName')
        self.assertEqual(len(response.context['books']), 2)
        self.assertEqual(response.context['total_books_count'], 3)
        self.assertEqual(response.context['has_next'], True)

    # ------------------------------------------------------------------------------------------------------------------
    def test_selected_author_invalid_request_method(self):
        response = self.anonymous_client.post(reverse('author', kwargs={'author_id': 10000}))

        self.assertEqual(response.resolver_match.func, selected_author)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_selected_author_not_exists(self):
        response = self.anonymous_client.get(reverse('author', kwargs={'author_id': 10000}))

        self.assertEqual(response.resolver_match.func, selected_author)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_selected_author(self):
        response = self.anonymous_client.get(reverse('author', kwargs={'author_id': self.author1.id}))

        self.assertEqual(response.resolver_match.func, selected_author)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'selected_author.html')
        self.assertIn('author', response.context)
        self.assertIn('books', response.context)
        self.assertEqual(response.context['author'].author_name, 'SomeAuthorCategoryName')
        self.assertEqual(response.context['author'].id, self.author1.id)
        self.assertEqual(len(response.context['books']), 1)
        self.assertEqual(response.context['books'][0].book_name, 'category_book_test1')

    # ------------------------------------------------------------------------------------------------------------------
    def test_sort_not_ajax(self):
        response = self.anonymous_client.get(reverse('book_sort'))

        self.assertEqual(response.resolver_match.func, sort)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_sort_category_not_int(self):
        response = self.anonymous_client.get(
            reverse('book_sort'),
            {'category': 'some_name'},
            HTTP_X_REQUESTED_WITH=self.xhr
        )
        self.assertEqual(response.resolver_match.func, sort)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_sort_missing_params(self):
        response = self.anonymous_client.get(
            reverse('book_sort'),
            {},
            HTTP_X_REQUESTED_WITH=self.xhr
        )
        self.assertEqual(response.resolver_match.func, sort)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_sort_form_validations_fails(self):
        response = self.anonymous_client.get(
            reverse('book_sort'),
            {'category': 1, 'criterion': 'a' * 35, 'page': -1},
            HTTP_X_REQUESTED_WITH=self.xhr
        )
        self.assertEqual(response.resolver_match.func, sort)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_sort_category_most_readable(self):
        response = self.anonymous_client.get(
            reverse('book_sort'),
            {'category': self.category.id, 'criterion': 'most_readable', 'page': 1},
            HTTP_X_REQUESTED_WITH=self.xhr
        )
        response_data = json.loads(response.content.decode('utf-8'))

        expected_response = {
            'category': self.category.id,
            'criterion': 'most_readable',
            'books': [
                {
                    'id': self.book1.id,
                    'name': self.book1.book_name,
                    'author': self.book1.id_author.author_name,
                    'url': ''
                },
                {
                    'id': self.book2.id,
                    'name': self.book2.book_name,
                    'author': self.book2.id_author.author_name,
                    'url': ''
                }
            ],
            'has_next': False,
            'next_page': 1
        }
        self.assertEqual(response.resolver_match.func, sort)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, expected_response)

    # ------------------------------------------------------------------------------------------------------------------
    def test_sort_by_rating_first_page(self):
        response = self.anonymous_client.get(
            reverse('book_sort'),
            {'category': self.category.id, 'criterion': 'estimation', 'page': 1},
            HTTP_X_REQUESTED_WITH=self.xhr
        )
        response_data = json.loads(response.content.decode('utf-8'))

        expected_response = {
            'category': self.category.id,
            'criterion': 'estimation',
            'books': [
                {
                    'id': self.book3.id,
                    'name': self.book3.book_name,
                    'author': self.book3.id_author.author_name,
                    'url': '',
                    'rating': 10.0
                },
                {
                    'id': self.book2.id,
                    'name': self.book2.book_name,
                    'author': self.book2.id_author.author_name,
                    'url': '',
                    'rating': 7.0
                }
            ],
            'has_next': True,
            'next_page': 2
        }
        self.assertEqual(response.resolver_match.func, sort)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, expected_response)

    # ------------------------------------------------------------------------------------------------------------------
    def test_sort_by_rating_last_page(self):
        response = self.anonymous_client.get(
            reverse('book_sort'),
            {'category': self.category.id, 'criterion': 'estimation', 'page': 2},
            HTTP_X_REQUESTED_WITH=self.xhr
        )
        response_data = json.loads(response.content.decode('utf-8'))

        expected_response = {
            'category': self.category.id,
            'criterion': 'estimation',
            'books': [
                {
                    'id': self.book1.id,
                    'name': self.book1.book_name,
                    'author': self.book1.id_author.author_name,
                    'url': '',
                    'rating': 5.0
                }
            ],
            'has_next': False,
            'next_page': 2
        }
        self.assertEqual(response.resolver_match.func, sort)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, expected_response)

    # ------------------------------------------------------------------------------------------------------------------
    def test_find_books_not_ajax(self):
        response = self.anonymous_client.get(reverse('search_book_app'))

        self.assertEqual(response.resolver_match.func, find_books)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_find_books_no_data(self):
        response = self.anonymous_client.get(
            reverse('search_book_app'),
            {'page': 1},
            HTTP_X_REQUESTED_WITH=self.xhr
        )

        self.assertEqual(response.resolver_match.func, find_books)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_find_books_too_long_data(self):
        response = self.anonymous_client.get(
            reverse('search_book_app'),
            {'data': 'aa' * 200, 'page': 1},
            HTTP_X_REQUESTED_WITH=self.xhr
        )

        self.assertEqual(response.resolver_match.func, find_books)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_find_books_missing_page(self):
        response = self.anonymous_client.get(
            reverse('search_book_app'),
            {'data': 'test'},
            HTTP_X_REQUESTED_WITH=self.xhr
        )

        self.assertEqual(response.resolver_match.func, find_books)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_find_books_negative_page(self):
        response = self.anonymous_client.get(
            reverse('search_book_app'),
            {'data': 'test', 'page': -1},
            HTTP_X_REQUESTED_WITH=self.xhr
        )

        self.assertEqual(response.resolver_match.func, find_books)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_find_books_no_matches(self):
        response = self.anonymous_client.get(
            reverse('search_book_app'),
            {'data': 'not_existing', 'page': 1},
            HTTP_X_REQUESTED_WITH=self.xhr
        )
        response_data = json.loads(response.content.decode('utf-8'))

        expected_response = {
            'books': [],
            'has_next': False,
            'next_page': 1
        }

        self.assertEqual(response.resolver_match.func, find_books)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, expected_response)

    # ------------------------------------------------------------------------------------------------------------------
    def test_find_books_matches_found_first_page(self):
        response = self.anonymous_client.get(
            reverse('search_book_app'),
            {'data': 'category_book_test', 'page': 1},
            HTTP_X_REQUESTED_WITH=self.xhr
        )
        response_data = json.loads(response.content.decode('utf-8'))
        expected_response = {
            'books': [
                {
                    'id': self.book1.id,
                    'name': self.book1.book_name,
                    'author': self.book1.id_author.author_name,
                    'url': ''
                },
                {
                    'id': self.book2.id,
                    'name': self.book2.book_name,
                    'author': self.book2.id_author.author_name,
                    'url': ''
                }
            ],
            'has_next': True,
            'next_page': 2
        }

        self.assertEqual(response.resolver_match.func, find_books)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, expected_response)

    # ------------------------------------------------------------------------------------------------------------------
    def test_find_books_matches_found_last_page(self):
        response = self.anonymous_client.get(
            reverse('search_book_app'),
            {'data': 'category_book_test', 'page': 2},
            HTTP_X_REQUESTED_WITH=self.xhr
        )
        response_data = json.loads(response.content.decode('utf-8'))

        expected_response = {
            'books': [
                {
                    'id': self.book3.id,
                    'name': self.book3.book_name,
                    'author': self.book3.id_author.author_name,
                    'url': ''
                }
            ],
            'has_next': False,
            'next_page': 2
        }

        self.assertEqual(response.resolver_match.func, find_books)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, expected_response)

    # ------------------------------------------------------------------------------------------------------------------
    def test_load_books_not_ajax(self):
        response = self.anonymous_client.get(reverse('load_books', kwargs={'category_id': self.category.id}))

        self.assertEqual(response.resolver_match.func, load_books)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_load_books_missing_page_param(self):
        response = self.anonymous_client.get(
            reverse('load_books', kwargs={'category_id': self.category.id}),
            {},
            HTTP_X_REQUESTED_WITH=self.xhr
        )

        self.assertEqual(response.resolver_match.func, load_books)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_load_books_negative_page_param(self):
        response = self.anonymous_client.get(
            reverse('load_books', kwargs={'category_id': self.category.id}),
            {'page': -15},
            HTTP_X_REQUESTED_WITH=self.xhr
        )

        self.assertEqual(response.resolver_match.func, load_books)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_load_books_success(self):
        response = self.anonymous_client.get(
            reverse('load_books', kwargs={'category_id': self.category.id}),
            {'page': 2},
            HTTP_X_REQUESTED_WITH=self.xhr
        )
        response_data = json.loads(response.content.decode('utf-8'))

        expected_books = [
            {
                'id': self.book3.id,
                'name': self.book3.book_name,
                'author': self.book3.id_author.author_name,
                'url': ''
            }
        ]

        self.assertEqual(response.resolver_match.func, load_books)
        self.assertEqual(response.status_code, 200)
        self.assertIn('category_id', response_data)
        self.assertIn('books', response_data)
        self.assertIn('has_next', response_data)
        self.assertIn('next_page', response_data)
        self.assertEqual(response_data['category_id'], str(self.category.id))
        self.assertEqual(list(response_data['books']), expected_books)
        self.assertEqual(response_data['has_next'], False)
        self.assertEqual(response_data['next_page'], 2)


