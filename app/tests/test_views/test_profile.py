# -*- coding: utf-8 -*-

import json
import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.test import TestCase, Client

from ...models import Book, TheUser, Category, Language, Author, AddedBook
from ...views.profile_views import profile, upload_avatar, change_password

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(TEST_DIR, '../fixtures')


# ----------------------------------------------------------------------------------------------------------------------
class ProfileViewsTest(TestCase):

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def setUpTestData(cls):
        cls.xhr = 'XMLHttpRequest'

        cls.user1 = User.objects.create_user(username='profile_user1', email='profile_user1@user.com', password='Dummy')
        cls.user2 = User.objects.create_user(username='profile_user2', email='profile_user2@user.com', password='Dummy')
        cls.the_user1 = TheUser.objects.get(id_user=cls.user1)
        cls.the_user2 = TheUser.objects.get(id_user=cls.user2)

        cls.category = Category.objects.create(category_name='Category_name')
        cls.language = Language.objects.create(language='English')
        cls.author = Author.objects.create(author_name='Author_name')

        cls.generate_books()
        cls.added_book1 = AddedBook.objects.create(id_book=cls.book1, id_user=cls.the_user1)
        cls.added_book2 = AddedBook.objects.create(id_book=cls.book2, id_user=cls.the_user1)

        cls.anonymous_client = Client()
        cls.logged_client = Client()
        cls.logged_client.login(username='profile_user1', password='Dummy')

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def tearDownClass(cls):
        for book in Book.objects.all():
            if os.path.exists(book.book_file.path):
                os.remove(book.book_file.path)
            if book.photo and os.path.exists(book.photo.path):
                os.remove(book.photo.path)

        if cls.the_user1.user_photo and os.path.exists(cls.the_user1.user_photo.path):
            os.remove(cls.the_user1.user_photo.path)

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def generate_books(cls):
        test_book_path = os.path.join(TEST_DATA_DIR, 'test_book.pdf')

        cls.book1 = Book.objects.create(
            book_name='Profile_test_book_1',
            id_author=cls.author,
            id_category=cls.category,
            language=cls.language,
            book_file=SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
            who_added=cls.the_user1
        )
        cls.book2 = Book.objects.create(
            book_name='Profile_test_book_2',
            id_author=cls.author,
            id_category=cls.category,
            language=cls.language,
            book_file=SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
            who_added=cls.the_user2
        )

    # ------------------------------------------------------------------------------------------------------------------
    def test_profile_not_get_method(self):
        response = self.logged_client.post(reverse('profile', kwargs={'profile_id': self.user1.id}))

        self.assertEqual(response.resolver_match.func, profile)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_profile_not_authenticated_user(self):
        response = self.anonymous_client.get(reverse('profile', kwargs={'profile_id': self.user1.id}))

        self.assertEqual(response.resolver_match.func, profile)
        self.assertRedirects(response, reverse('index'), status_code=302, target_status_code=200)

    # ------------------------------------------------------------------------------------------------------------------
    def test_profile_not_existing_user(self):
        response = self.logged_client.get(reverse('profile', kwargs={'profile_id': self.user1.id * 9999}))

        self.assertEqual(response.resolver_match.func, profile)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_profile_success_owner(self):
        response = self.logged_client.get(reverse('profile', kwargs={'profile_id': self.user1.id}))

        self.assertEqual(response.resolver_match.func, profile)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertTrue('owner' in response.context)
        self.assertEqual(response.context['profile_user'], self.the_user1)
        self.assertEqual(len(response.context['added_books']), 2)
        self.assertEqual(response.context['added_books'][0].id_book, self.book1)
        self.assertEqual(response.context['added_books'][1].id_book, self.book2)
        self.assertEqual(len(response.context['uploaded_books']), 1)
        self.assertEqual(response.context['uploaded_books'][0], self.book1)
        self.assertTrue(isinstance(response.context['img_random'], int))
        self.assertTrue(1000 >= response.context['img_random'] >= 0)

    # ------------------------------------------------------------------------------------------------------------------
    def test_profile_success_not_owner(self):
        response = self.logged_client.get(reverse('profile', kwargs={'profile_id': self.user2.id}))

        self.assertEqual(response.resolver_match.func, profile)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertFalse('owner' in response.context)
        self.assertEqual(response.context['profile_user'], self.the_user2)
        self.assertEqual(len(response.context['added_books']), 0)
        self.assertEqual(len(response.context['uploaded_books']), 1)
        self.assertEqual(response.context['uploaded_books'][0], self.book2)
        self.assertTrue(isinstance(response.context['img_random'], int))
        self.assertTrue(1000 >= response.context['img_random'] >= 0)

    # ------------------------------------------------------------------------------------------------------------------
    def test_change_avatar_not_ajax(self):
        response = self.logged_client.post(reverse('upload_avatar'), {})

        self.assertEqual(response.resolver_match.func, upload_avatar)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_change_avatar_missing_params(self):
        response = self.logged_client.post(reverse('upload_avatar'), {}, HTTP_X_REQUESTED_WITH=self.xhr)

        self.assertEqual(response.resolver_match.func, upload_avatar)
        self.assertEqual(response.status_code, 500)

    # ------------------------------------------------------------------------------------------------------------------
    def test_change_avatar_invalid_params(self):
        image_path = os.path.join(TEST_DATA_DIR, 'test_book.pdf')

        response = self.logged_client.post(
            reverse('upload_avatar'),
            {'avatar': SimpleUploadedFile('test_book.pdf', open(image_path, 'rb').read())},
            HTTP_X_REQUESTED_WITH=self.xhr
        )
        self.assertEqual(response.resolver_match.func, upload_avatar)
        self.assertEqual(response.status_code, 500)

    # ------------------------------------------------------------------------------------------------------------------
    def test_change_avatar_success(self):
        image_path = os.path.join(TEST_DATA_DIR, 'test_book_image.png')

        response = self.logged_client.post(
            reverse('upload_avatar'),
            {'avatar': SimpleUploadedFile('test_book.pdf', open(image_path, 'rb').read())},
            HTTP_X_REQUESTED_WITH=self.xhr
        )
        response_data = json.loads(response.content.decode('utf-8'))
        avatar_path = os.path.join(settings.MEDIA_ROOT, 'user', 'user_{}.png'.format(self.user1.id))

        self.assertEqual(response.resolver_match.func, upload_avatar)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response_data.get('message', False))
        self.assertEqual(response_data['message'], 'Аватар успешно изменен!')
        self.assertTrue(os.path.exists(avatar_path))
        self.assertTrue(TheUser.objects.get(id=self.the_user1.id).user_photo)

    # ------------------------------------------------------------------------------------------------------------------
    def test_change_password_not_ajax(self):
        response = self.logged_client.post(reverse('change_password'), {})

        self.assertEqual(response.resolver_match.func, change_password)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_change_password_missing_params(self):
        response = self.logged_client.post(reverse('change_password'), {}, HTTP_X_REQUESTED_WITH=self.xhr)

        self.assertEqual(response.resolver_match.func, change_password)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_change_password_invalid_params(self):
        response = self.logged_client.post(
            reverse('change_password'),
            {'prev_password': 'extremely_long_prev_password', 'new_password': 'extremely_long_new_password'},
            HTTP_X_REQUESTED_WITH=self.xhr
        )

        self.assertEqual(response.resolver_match.func, change_password)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_change_password_prev_passowrd_not_match(self):
        response = self.logged_client.post(
            reverse('change_password'),
            {'prev_password': 'Bad_password', 'new_password': 'the_new_password'},
            HTTP_X_REQUESTED_WITH=self.xhr
        )
        response_data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.resolver_match.func, change_password)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response_data, str))
        self.assertEqual(response_data, 'Старый пароль не совпадает. Проверьте на наличие ошибок.')

    # ------------------------------------------------------------------------------------------------------------------
    def test_change_password_success(self):
        self.assertTrue(self.user1.check_password('Dummy'))

        response = self.logged_client.post(
            reverse('change_password'),
            {'prev_password': 'Dummy', 'new_password': 'the_new_password'},
            HTTP_X_REQUESTED_WITH=self.xhr
        )
        response_data = json.loads(response.content.decode('utf-8'))

        updated_user = User.objects.get(id=self.user1.id)

        self.assertEqual(response.resolver_match.func, change_password)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response_data, str))
        self.assertEqual(response_data, 'Пароль успешно изменен!')
        self.assertTrue(updated_user.check_password('the_new_password'))
