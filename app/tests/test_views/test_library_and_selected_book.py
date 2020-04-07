# -*- coding: utf-8 -*-

import json
import os

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from django.test import TestCase, Client, override_settings

from ...forms import ReportForm
from ...models import Author, Book, AddedBook, Category, Language, TheUser, BookRating, BookComment
from ...views.library_views import all_categories, selected_category, selected_author, sort, find_books, load_books
from ...views.selected_book_views import (
    selected_book, add_book_to_home, remove_book_from_home, change_rating, add_comment, load_comments, report_book
)
from ..utils import Utils

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
        cls.user2 = User.objects.create_user(username='libusername2', email='lib2@user.com', password='password')
        cls.the_user = TheUser.objects.get(id_user=cls.user)
        cls.the_user2 = TheUser.objects.get(id_user=cls.user2)

        cls.anonymous_client = Client()
        cls.logged_client = Client()
        cls.logged_client.login(username='libusername', password='password')
        cls.logged_client2 = Client()
        cls.logged_client2.login(username='libusername2', password='password')

        cls.category = Category.objects.create(category_name='CustomCategoryName')
        cls.language = Language.objects.create(language='French')
        cls.author1 = Author.objects.create(author_name='SomeAuthorCategoryName')
        cls.author2 = Author.objects.create(author_name='SomeOtherCategoryNameAuthor<>&"')

        cls.book1 = Book.objects.create(
            book_name='category_book_test1',
            id_author=cls.author1,
            id_category=cls.category,
            language=cls.language,
            book_file=SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
            who_added=cls.the_user
        )
        cls.book2 = Book.objects.create(
            book_name='category_book_test2<>&"',
            id_author=cls.author2,
            id_category=cls.category,
            language=cls.language,
            book_file=SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
            who_added=cls.the_user
        )
        cls.book3 = Book.objects.create(
            book_name='category_book_test3<>&"',
            id_author=cls.author2,
            id_category=cls.category,
            language=cls.language,
            book_file=SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
            who_added=cls.the_user
        )
        cls.book4 = Book.objects.create(
            book_name='category_book_test4<>&"',
            id_author=cls.author2,
            id_category=cls.category,
            language=cls.language,
            book_file=SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
            who_added=cls.the_user,
            private_book=True
        )
        cls.book5 = Book.objects.create(
            book_name='category_book_test5<>&"',
            id_author=cls.author2,
            id_category=cls.category,
            language=cls.language,
            book_file=SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
            who_added=cls.the_user,
            blocked_book=True
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
        self.assertEqual(response.context['total_books_count'], 5)
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
                    'name': 'category_book_test2&lt;&gt;&amp;&quot;',
                    'author': 'SomeOtherCategoryNameAuthor&lt;&gt;&amp;&quot;',
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
                    'name': 'category_book_test3&lt;&gt;&amp;&quot;',
                    'author': 'SomeOtherCategoryNameAuthor&lt;&gt;&amp;&quot;',
                    'url': '',
                    'rating': 10.0
                },
                {
                    'id': self.book2.id,
                    'name': 'category_book_test2&lt;&gt;&amp;&quot;',
                    'author': 'SomeOtherCategoryNameAuthor&lt;&gt;&amp;&quot;',
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
                },
                {
                    'id': self.book5.id,
                    'name': 'category_book_test5&lt;&gt;&amp;&quot;',
                    'author': 'SomeOtherCategoryNameAuthor&lt;&gt;&amp;&quot;',
                    'url': '',
                    'rating': None
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
                Utils.generate_sort_dict(self.book1),
                Utils.generate_sort_dict(self.book2)
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
                Utils.generate_sort_dict(self.book3),
                Utils.generate_sort_dict(self.book5)
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
            Utils.generate_sort_dict(self.book3),
            Utils.generate_sort_dict(self.book5)
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

    # ------------------------------------------------------------------------------------------------------------------
    # Selected Book test cases.
    # Done here due to issues with Django / MySQL closed connection...

    def test_selected_book_not_existing_book(self):
        response = self.logged_client.get(
            reverse('book', kwargs={'book_id': 50000})
        )
        self.assertEqual(response.resolver_match.func, selected_book)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_selected_book_is_private_for_anonymous_user(self):
        response = self.anonymous_client.get(
            reverse('book', kwargs={'book_id': self.book4.id})
        )
        self.assertEqual(response.resolver_match.func, selected_book)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_selected_book_is_private_for_logged_not_added_user(self):
        response = self.logged_client2.get(
            reverse('book', kwargs={'book_id': self.book4.id})
        )
        self.assertEqual(response.resolver_match.func, selected_book)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_selected_book_is_private_for_logged_who_added_user(self):
        response = self.logged_client.get(
            reverse('book', kwargs={'book_id': self.book4.id})
        )
        self.assertEqual(response.resolver_match.func, selected_book)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['book'], self.book4)
        self.assertIsNone(response.context['added_book'])
        self.assertEqual(response.context['added_book_count'], 0)
        self.assertEqual(len(response.context['comments']), 0)
        self.assertEqual(response.context['comments_page'], 1)
        self.assertFalse(response.context['comments_has_next_page'])
        self.assertEqual(response.context['book_rating'], '-')
        self.assertEqual(response.context['book_rating_count'], '')
        self.assertEqual(response.context['estimation_count'], range(1, 11))
        self.assertEqual(response.context['user'], self.the_user)
        self.assertEqual(len(response.context['recommend_books']), 0)
        self.assertIsNone(response.context['user_rated'])
        self.assertTrue(isinstance(response.context['report_form'], ReportForm))

    # ------------------------------------------------------------------------------------------------------------------
    def test_store_image(self):
        pass  # TODO add tests for storing images.

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_book_to_home_not_ajax(self):
        response = self.logged_client.post(reverse('add_book_home_app'), {})
        self.assertEqual(response.resolver_match.func, add_book_to_home)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_book_to_home_invalid_form_params(self):
        response = self.logged_client.post(
            reverse('add_book_home_app'), {'book': 'abc'}, HTTP_X_REQUESTED_WITH=self.xhr
        )
        self.assertEqual(response.resolver_match.func, add_book_to_home)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_book_to_home_private_book_not_wdo_added_user(self):
        response = self.logged_client2.post(
            reverse('add_book_home_app'), {'book': self.book4.id}, HTTP_X_REQUESTED_WITH=self.xhr
        )
        self.assertEqual(response.resolver_match.func, add_book_to_home)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_book_to_home_blocked_book(self):
        response = self.logged_client.post(
            reverse('add_book_home_app'), {'book': self.book5.id}, HTTP_X_REQUESTED_WITH=self.xhr
        )
        self.assertEqual(response.resolver_match.func, add_book_to_home)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_book_to_home_already_added_book(self):
        response = self.logged_client.post(
            reverse('add_book_home_app'), {'book': self.book1.id}, HTTP_X_REQUESTED_WITH=self.xhr
        )
        self.assertEqual(response.resolver_match.func, add_book_to_home)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_book_remove_from_home_not_ajax(self):
        response = self.logged_client.post(reverse('remove_book_home_app'), {})
        self.assertEqual(response.resolver_match.func, remove_book_from_home)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_remove_book_from_home_invalid_form_params(self):
        response = self.logged_client.post(
            reverse('remove_book_home_app'), {'book': 'abc'}, HTTP_X_REQUESTED_WITH=self.xhr
        )
        self.assertEqual(response.resolver_match.func, remove_book_from_home)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_remove_book_from_home_not_existing_book(self):
        response = self.logged_client.post(
            reverse('remove_book_home_app'), {'book': 10000}, HTTP_X_REQUESTED_WITH=self.xhr
        )
        self.assertEqual(response.resolver_match.func, remove_book_from_home)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_remove_book_from_home_not_existing_added_book(self):
        response = self.logged_client2.post(
            reverse('remove_book_home_app'), {'book': 10000}, HTTP_X_REQUESTED_WITH=self.xhr
        )
        self.assertEqual(response.resolver_match.func, remove_book_from_home)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_and_remove_book_from_home_success(self):
        response = self.logged_client.post(
            reverse('add_book_home_app'), {'book': self.book4.id}, HTTP_X_REQUESTED_WITH=self.xhr
        )
        self.assertEqual(response.resolver_match.func, add_book_to_home)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content.decode('utf-8')), {'book_id': self.book4.id})

        # Public book.
        response = self.logged_client.post(
            reverse('remove_book_home_app'), {'book': self.book4.id}, HTTP_X_REQUESTED_WITH=self.xhr
        )
        self.assertEqual(response.resolver_match.func, remove_book_from_home)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content.decode('utf-8')), True)

        # Blocked book.
        added_book = AddedBook.objects.create(id_book=self.book4, id_user=self.the_user)
        added_book.save()
        self.book4.blocked_book = True
        self.book4.save()

        response = self.logged_client.post(
            reverse('remove_book_home_app'), {'book': self.book4.id}, HTTP_X_REQUESTED_WITH=self.xhr
        )
        self.assertEqual(response.resolver_match.func, remove_book_from_home)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content.decode('utf-8')), False)

    # ------------------------------------------------------------------------------------------------------------------
    def test_change_rating_not_ajax(self):
        response = self.logged_client.post(reverse('change_rating_app'), {'book': self.book4.id, 'rating': 9})
        self.assertEqual(response.resolver_match.func, change_rating)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_change_rating_invalid_params(self):
        response = self.logged_client.post(
            reverse('change_rating_app'), {'book': 'abc', 'rating': 'abc'}, HTTP_X_REQUESTED_WITH=self.xhr
        )
        self.assertEqual(response.resolver_match.func, change_rating)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_change_rating_invalid_rating_value(self):
        response = self.logged_client.post(
            reverse('change_rating_app'), {'book': self.book4.id, 'rating': -1}, HTTP_X_REQUESTED_WITH=self.xhr
        )
        self.assertEqual(response.resolver_match.func, change_rating)
        self.assertEqual(response.status_code, 400)

        response = self.logged_client.post(
            reverse('change_rating_app'), {'book': self.book4.id, 'rating': 11}, HTTP_X_REQUESTED_WITH=self.xhr
        )
        self.assertEqual(response.resolver_match.func, change_rating)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_change_rating_success(self):
        # Not existing rating
        response = self.logged_client.post(
            reverse('change_rating_app'), {'book': self.book4.id, 'rating': 7}, HTTP_X_REQUESTED_WITH=self.xhr
        )
        self.assertEqual(response.resolver_match.func, change_rating)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content.decode('utf-8')), {'avg_rating': 7, 'rating_count': '(1)'})

        # Existing rating
        response = self.logged_client.post(
            reverse('change_rating_app'), {'book': self.book4.id, 'rating': 9}, HTTP_X_REQUESTED_WITH=self.xhr
        )
        self.assertEqual(response.resolver_match.func, change_rating)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content.decode('utf-8')), {'avg_rating': 9, 'rating_count': '(1)'})

        # Second user changed rating
        response = self.logged_client2.post(
            reverse('change_rating_app'), {'book': self.book4.id, 'rating': 4}, HTTP_X_REQUESTED_WITH=self.xhr
        )
        self.assertEqual(response.resolver_match.func, change_rating)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content.decode('utf-8')), {'avg_rating': 6.5, 'rating_count': '(2)'})

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_comment_not_ajax(self):
        response = self.logged_client.post(reverse('add_comment_app'), {})
        self.assertEqual(response.resolver_match.func, add_comment)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_comment_invalid_field_datatypes(self):
        response = self.logged_client.post(
            reverse('add_comment_app'), {'book': 'abc', 'comment': 'test'}, HTTP_X_REQUESTED_WITH=self.xhr
        )
        self.assertEqual(response.resolver_match.func, add_comment)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_comment_too_long_message(self):
        response = self.logged_client.post(
            reverse('add_comment_app'), {'book': self.book4.id, 'comment': 'test' * 200}, HTTP_X_REQUESTED_WITH=self.xhr
        )
        self.assertEqual(response.resolver_match.func, add_comment)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_comment_success(self):
        response = self.logged_client.post(
            reverse('add_comment_app'), {'book': self.book4.id, 'comment': 'test text'},
            HTTP_X_REQUESTED_WITH=self.xhr
        )
        comment = BookComment.objects.get(id_user=self.the_user, id_book=self.book4)
        self.assertEqual(response.resolver_match.func, add_comment)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content.decode('utf-8')),
            {
                'username': 'libusername',
                'user_photo': '',
                'posted_date': comment.posted_date.strftime('%d-%m-%Y'),
                'text': 'test text'
            }
        )

    # ------------------------------------------------------------------------------------------------------------------
    def test_load_comments_not_ajax(self):
        response = self.logged_client.post(reverse('load_comments_app'), {})
        self.assertEqual(response.resolver_match.func, load_comments)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_load_comments_invalid_form_parameters(self):
        response = self.logged_client.post(
            reverse('load_comments_app'), {'page': 'abc', 'book_id': 'abc'}, HTTP_X_REQUESTED_WITH=self.xhr
        )
        self.assertEqual(response.resolver_match.func, load_comments)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_load_comments_success(self):
        # Create some test comments.
        for i in range(50):
            response = self.logged_client.post(
                reverse('add_comment_app'),
                {'book': self.book1.id, 'comment': 'test{}'.format(i)},
                HTTP_X_REQUESTED_WITH=self.xhr
            )
            self.assertEqual(response.status_code, 200)

        # Testing first page (i.e. second, because first already loaded).
        response = self.logged_client.post(
            reverse('load_comments_app'), {'page': 1, 'book_id': self.book1.id}, HTTP_X_REQUESTED_WITH=self.xhr
        )
        response_data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.resolver_match.func, load_comments)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['current_page'], 2)
        self.assertEqual(response_data['has_next_page'], True)
        self.assertEqual(response_data['book_id'], self.book1.id)
        self.assertEqual(len(response_data['comments']), 20)

        self.assertEqual(response_data['comments'][0]['username'], self.user.username)
        self.assertEqual(response_data['comments'][0]['user_photo'], '')
        self.assertIn('posted_date', response_data['comments'][0])
        self.assertEqual(response_data['comments'][0]['text'], 'test29')
        self.assertEqual(response_data['comments'][19]['username'], self.user.username)
        self.assertEqual(response_data['comments'][19]['user_photo'], '')
        self.assertIn('posted_date', response_data['comments'][19])
        self.assertEqual(response_data['comments'][19]['text'], 'test10')

        # Testing second page.
        response = self.logged_client.post(
            reverse('load_comments_app'), {'page': 2, 'book_id': self.book1.id}, HTTP_X_REQUESTED_WITH=self.xhr
        )
        response_data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.resolver_match.func, load_comments)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['current_page'], 3)
        self.assertEqual(response_data['has_next_page'], False)
        self.assertEqual(response_data['book_id'], self.book1.id)
        self.assertEqual(len(response_data['comments']), 10)

        self.assertEqual(response_data['comments'][0]['username'], self.user.username)
        self.assertEqual(response_data['comments'][0]['user_photo'], '')
        self.assertIn('posted_date', response_data['comments'][0])
        self.assertEqual(response_data['comments'][0]['text'], 'test9')
        self.assertEqual(response_data['comments'][9]['username'], self.user.username)
        self.assertEqual(response_data['comments'][9]['user_photo'], '')
        self.assertIn('posted_date', response_data['comments'][9])
        self.assertEqual(response_data['comments'][9]['text'], 'test0')

    # ------------------------------------------------------------------------------------------------------------------
    def test_report_book_not_post_request(self):
        response = self.logged_client.get(reverse('report-book'), {}, HTTP_X_REQUESTED_WITH=self.xhr)
        self.assertEqual(response.resolver_match.func, report_book)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_report_book_too_long_message(self):
        response = self.logged_client.post(
            reverse('report-book'), {'text': 'test text' * 1000}, HTTP_X_REQUESTED_WITH=self.xhr
        )
        self.assertEqual(response.resolver_match.func, report_book)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_report_book_success(self):
        response = self.logged_client.post(
            reverse('report-book'), {'text': 'test text success'}, HTTP_X_REQUESTED_WITH=self.xhr
        )
        self.assertEqual(response.resolver_match.func, report_book)
        self.assertEqual(response.status_code, 200)
