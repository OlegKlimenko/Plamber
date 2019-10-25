# -*- coding: utf-8 -*-

import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from django.test import TestCase

from rest_framework.test import APIClient

from ...views.selected_book_views import add_book_to_home
from app.models import TheUser, Book, Category, Language, Author, AddedBook

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(TEST_DIR, '../fixtures')


# ----------------------------------------------------------------------------------------------------------------------
class SelectedBookViewsTestCase(TestCase):

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def setUpTestData(cls):
        cls.invalid_user_token = 'ff3e368d-0000-0000-0000-44545315c737'
        cls.user = User.objects.create_user(
            username='api_selected_book', email='api_selected_book@email.com', password='123456'
        )
        cls.other_user = User.objects.create_user(
            username='api_selected_book_other', email='api_selected_book_other@email.com', password='123456'
        )
        cls.the_user = TheUser.objects.get(id_user=cls.user)
        cls.the_other_user = TheUser.objects.get(id_user=cls.other_user)

        cls.client = APIClient()
        cls.api_key = settings.API_SECRET_KEY

        cls.category = Category.objects.create(category_name='selected_api_category')
        cls.language = Language.objects.create(language='selected_api_language')
        cls.author = Author.objects.create(author_name='selected_api_author')

        test_book_path = os.path.join(TEST_DATA_DIR, 'test_book.pdf')

        books_setup = [
            ('selected_api_1', cls.the_user, False, False),
            ('selected_api_2', cls.the_user, False, False),
            ('selected_api_private_book', cls.the_other_user, True, False),
            ('selected_api_blocked_book', cls.the_user, False, True),
            ('selected_api_already_addded', cls.the_user, False, False)
        ]

        for (book_name, who_added, is_private, is_blocked) in books_setup:
            Book.objects.create(
                book_name=book_name,
                id_author=cls.author,
                id_category=cls.category,
                language=cls.language,
                book_file=SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
                who_added=who_added,
                private_book=is_private,
                blocked_book=is_blocked
            )

        cls.book_which_added = Book.objects.get(book_name='selected_api_already_addded')

        AddedBook.objects.create(id_book=cls.book_which_added, id_user=cls.the_user)

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def tearDownClass(cls):
        for book in Book.objects.all():
            if os.path.exists(book.book_file.path):
                os.remove(book.book_file.path)
            if book.photo and os.path.exists(book.photo.path):
                os.remove(book.photo.path)

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_book_home_not_valid_app_key(self):
        payload = {'app_key': 'dummy_key', 'username': 'api_selected_book'}
        response = self.client.post(reverse('add_book_home_api'), payload)

        self.assertEqual(response.resolver_match.func, add_book_to_home)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_book_home_negative_book_id(self):
        payload = {'app_key': self.api_key, 'book_id': -10, 'user_token': self.the_user.auth_token}
        response = self.client.post(reverse('add_book_home_api'), payload)

        expected_data = {
            'data': {},
            'detail': {
                'book_id': ['Ensure this value is greater than or equal to 1.']
            }
        }
        self.assertEqual(response.resolver_match.func, add_book_to_home)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, expected_data)

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_book_home_not_number_book_id(self):
        payload = {'app_key': self.api_key, 'book_id': 'word', 'user_token': self.the_user.auth_token}
        response = self.client.post(reverse('add_book_home_api'), payload)

        expected_data = {
            'data': {},
            'detail': {
                'book_id': ['A valid integer is required.']
            }
        }
        self.assertEqual(response.resolver_match.func, add_book_to_home)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, expected_data)

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_book_home_no_user_token(self):
        payload = {'app_key': self.api_key, 'book_id': 13}
        response = self.client.post(reverse('add_book_home_api'), payload)

        expected_data = {
            'data': {},
            'detail': {
                'user_token': ['This field is required.']
            }
        }
        self.assertEqual(response.resolver_match.func, add_book_to_home)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, expected_data)

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_book_home_no_user_object(self):
        payload = {'app_key': self.api_key, 'book_id': 13, 'user_token': self.invalid_user_token}
        response = self.client.post(reverse('add_book_home_api'), payload)

        self.assertEqual(response.resolver_match.func, add_book_to_home)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {'detail': 'Not found.'})

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_book_home_no_book_object(self):
        payload = {'app_key': self.api_key, 'book_id': 9999, 'user_token': self.the_user.auth_token}
        response = self.client.post(reverse('add_book_home_api'), payload)

        self.assertEqual(response.resolver_match.func, add_book_to_home)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {'detail': 'Not found.'})

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_book_private_book_of_other_user(self):
        book = Book.objects.get(book_name='selected_api_private_book')

        payload = {'app_key': self.api_key, 'book_id': book.id, 'user_token': self.the_user.auth_token}
        response = self.client.post(reverse('add_book_home_api'), payload)

        self.assertEqual(response.resolver_match.func, add_book_to_home)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {})

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_book_blocked_book(self):
        book = Book.objects.get(book_name='selected_api_blocked_book')

        payload = {'app_key': self.api_key, 'book_id': book.id, 'user_token': self.the_user.auth_token}
        response = self.client.post(reverse('add_book_home_api'), payload)

        self.assertEqual(response.resolver_match.func, add_book_to_home)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'detail': 'This book is blocked'})

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_book_already_added_book(self):
        book = Book.objects.get(book_name='selected_api_already_addded')

        payload = {'app_key': self.api_key, 'book_id': book.id, 'user_token': self.the_user.auth_token}
        response = self.client.post(reverse('add_book_home_api'), payload)

        self.assertEqual(response.resolver_match.func, add_book_to_home)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {})

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_book_success(self):
        book = Book.objects.get(book_name='selected_api_2')

        payload = {'app_key': self.api_key, 'book_id': book.id, 'user_token': self.the_user.auth_token}
        response = self.client.post(reverse('add_book_home_api'), payload)

        self.assertEqual(response.resolver_match.func, add_book_to_home)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'detail': 'success', 'data': {}})
        self.assertTrue(AddedBook.objects.filter(id_book=book, id_user=self.the_user).exists())
