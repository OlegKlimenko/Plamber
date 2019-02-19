# -*- coding: utf-8 -*-

import json
import os
from unittest.mock import patch, Mock

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from django.test import TestCase, Client

from ...models import Author, Book, AddedBook, Category, Language, TheUser
from ...views.index_views import index, is_user_exists, is_mail_exists, sign_in, restore_data

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(TEST_DIR, '../fixtures')


# ----------------------------------------------------------------------------------------------------------------------
class IndexViewsTest(TestCase):

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def setUpTestData(cls):
        test_book_path = os.path.join(TEST_DATA_DIR, 'test_book.pdf')

        cls.xhr = 'XMLHttpRequest'
        cls.user = User.objects.create_user(username='index_user', email='index@user.com', password='password')
        cls.the_user = TheUser.objects.get(id_user=cls.user)

        cls.anonymous_client = Client()
        cls.logged_client = Client()
        cls.logged_client.login(username='index_user', password='password')

        cls.category = Category.objects.create(category_name='Category_name')
        cls.language = Language.objects.create(language='English')
        cls.author = Author.objects.create(author_name='Author_name')

        cls.book1 = Book.objects.create(
            book_name='index_book_test1',
            id_author=cls.author,
            id_category=cls.category,
            language=cls.language,
            book_file=SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
            who_added=cls.the_user
        )
        cls.book2 = Book.objects.create(
            book_name='index_book_test2',
            id_author=cls.author,
            id_category=cls.category,
            language=cls.language,
            book_file=SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
            who_added=cls.the_user
        )

        AddedBook.objects.create(id_user=cls.the_user, id_book=cls.book1)
        AddedBook.objects.create(id_user=cls.the_user, id_book=cls.book2)

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def tearDownClass(cls):
        for book in Book.objects.all():
            if os.path.exists(book.book_file.path):
                os.remove(book.book_file.path)
            if book.photo and os.path.exists(book.photo.path):
                os.remove(book.photo.path)

    # ------------------------------------------------------------------------------------------------------------------
    def test_index_get_not_logged_user(self):
        response = self.anonymous_client.get(reverse('index'))

        self.assertEqual(response.resolver_match.func, index)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    # ------------------------------------------------------------------------------------------------------------------
    def test_index_get_logged_user(self):
        response = self.logged_client.get(reverse('index'))

        self.assertEqual(response.resolver_match.func, index)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertEqual(len(response.context['books']), 2)
        self.assertFalse(len(response.context['recommend_books']))

    # ------------------------------------------------------------------------------------------------------------------
    def test_user_login_missing_params(self):
        response = self.anonymous_client.post(reverse('index'))

        self.assertEqual(response.resolver_match.func, index)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertTrue('invalid_authentication' in response.context)
        self.assertTrue(response.context['invalid_authentication'])

    # ------------------------------------------------------------------------------------------------------------------
    def test_user_login_incorrect_param_names(self):
        response = self.anonymous_client.post(reverse('index'), {'user': 'possible_username',
                                                                 'password': 'DummyPassword'})

        self.assertEqual(response.resolver_match.func, index)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertTrue('invalid_authentication' in response.context)
        self.assertTrue(response.context['invalid_authentication'])

    # ------------------------------------------------------------------------------------------------------------------
    def test_index_login_very_long_username_param(self):
        response = self.anonymous_client.post(reverse('index'), {'username': 'dummytestusernameverylongnametwoobiig',
                                                                 'passw': 'DummyPassword'})
        self.assertEqual(response.resolver_match.func, index)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertTrue('invalid_authentication' in response.context)
        self.assertTrue(response.context['invalid_authentication'])

    # ------------------------------------------------------------------------------------------------------------------
    def test_user_login_invalid_regex_username(self):
        username_patterns = [
            'ab#$@cdev', '#$@username', 'username%#&#&', 'db24!!!db34', '#$@234234', '#123dkf%'
        ]

        for pattern in username_patterns:
            with self.subTest(pattern=pattern):
                response = self.anonymous_client.post(reverse('index'), {'username': pattern,
                                                                         'passw': 'DummyPassword'})
                self.assertEqual(response.resolver_match.func, index)
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, 'index.html')
                self.assertTrue('invalid_authentication' in response.context)
                self.assertTrue(response.context['invalid_authentication'])

    # ------------------------------------------------------------------------------------------------------------------
    def test_user_login_invalid_regex_email(self):
        email_patterns = [
            'no_extension@ddd', '@first.missing', 'after_at_miss@', '$%#@474**.om', 'em#$@ail@m.com', '#em@ail@m.com'
        ]

        for pattern in email_patterns:
            with self.subTest(pattern=pattern):
                response = self.anonymous_client.post(reverse('index'), {'username': pattern,
                                                                         'passw': 'DummyPassword'})
                self.assertEqual(response.resolver_match.func, index)
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, 'index.html')
                self.assertTrue('invalid_authentication' in response.context)
                self.assertTrue(response.context['invalid_authentication'])

    # ------------------------------------------------------------------------------------------------------------------
    def test_user_login_very_long_password_param(self):
        response = self.anonymous_client.post(reverse('index'), {'username': 'allowed_username',
                                                                 'passw': 'extremelyveryverylongpasswordnotallow'})
        self.assertEqual(response.resolver_match.func, index)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertTrue('invalid_authentication' in response.context)
        self.assertTrue(response.context['invalid_authentication'])

    # ------------------------------------------------------------------------------------------------------------------
    def test_user_login_valid_username_not_existing_user(self):
        response = self.anonymous_client.post(reverse('index'), {'username': 'not_existing_username',
                                                                 'passw': 'DummyPassword'})
        self.assertEqual(response.resolver_match.func, index)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertTrue('invalid_authentication' in response.context)
        self.assertTrue(response.context['invalid_authentication'])

    # ------------------------------------------------------------------------------------------------------------------
    def test_user_login_valid_email_not_existing_user(self):
        response = self.anonymous_client.post(reverse('index'), {'username': 'test@email.com',
                                                                 'passw': 'DummyPassword'})
        self.assertEqual(response.resolver_match.func, index)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertTrue('invalid_authentication' in response.context)
        self.assertTrue(response.context['invalid_authentication'])

    # ------------------------------------------------------------------------------------------------------------------
    def test_user_login_with_username_success(self):
        response = self.anonymous_client.post(reverse('index'), {'username': 'index_user',
                                                                 'passw': 'password'})
        self.assertEqual(response.resolver_match.func, index)
        self.assertRedirects(response, reverse('index'), status_code=302, target_status_code=200)

        response = self.anonymous_client.get(reverse('index'))
        self.assertEqual(response.resolver_match.func, index)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertEqual(len(response.context['books']), 2)
        self.assertFalse(len(response.context['recommend_books']))

    # ------------------------------------------------------------------------------------------------------------------
    def test_user_login_with_email_success(self):
        response = self.anonymous_client.post(reverse('index'), {'username': 'index@user.com',
                                                                 'passw': 'password'})
        self.assertEqual(response.resolver_match.func, index)
        self.assertRedirects(response, reverse('index'), status_code=302, target_status_code=200)

        response = self.anonymous_client.get(reverse('index'))
        self.assertEqual(response.resolver_match.func, index)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertEqual(len(response.context['books']), 2)
        self.assertFalse(len(response.context['recommend_books']))


    # ------------------------------------------------------------------------------------------------------------------
    def test_is_user_exists_not_ajax(self):
        response = self.logged_client.get(reverse('is_user_exists'), {'username': 'test_username'})

        self.assertEqual(response.resolver_match.func, is_user_exists)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_is_user_exists_missing_param(self):
        response = self.logged_client.get(reverse('is_user_exists'), {}, HTTP_X_REQUESTED_WITH=self.xhr)

        self.assertEqual(response.resolver_match.func, is_user_exists)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_is_user_exists_invalid_params(self):
        response = self.logged_client.get(reverse('is_user_exists'), {'username': 'test_name' * 20},  # Very long
                                          HTTP_X_REQUESTED_WITH=self.xhr)
        self.assertEqual(response.resolver_match.func, is_user_exists)
        self.assertEqual(response.status_code, 404)

        response = self.logged_client.get(reverse('is_user_exists'), {'username': 'a'},  # Very short
                                          HTTP_X_REQUESTED_WITH=self.xhr)
        self.assertEqual(response.resolver_match.func, is_user_exists)
        self.assertEqual(response.status_code, 404)

        response = self.logged_client.get(reverse('is_user_exists'), {'username': 'a#$(#*test_na'},  # Regex not match
                                          HTTP_X_REQUESTED_WITH=self.xhr)
        self.assertEqual(response.resolver_match.func, is_user_exists)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_user_exists_successful_no_user_match(self):
        response = self.logged_client.get(reverse('is_user_exists'), {'username': 'test_name'},
                                          HTTP_X_REQUESTED_WITH=self.xhr)
        response_data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.resolver_match.func, is_user_exists)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, False)

    # ------------------------------------------------------------------------------------------------------------------
    def test_user_exists_successful_user_match(self):
        response = self.logged_client.get(reverse('is_user_exists'), {'username': 'index_user'},
                                          HTTP_X_REQUESTED_WITH=self.xhr)
        response_data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.resolver_match.func, is_user_exists)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, True)

    # ------------------------------------------------------------------------------------------------------------------
    def test_is_mail_exists_not_ajax(self):
        response = self.logged_client.get(reverse('is_mail_exists'), {'email': 'test_username'})

        self.assertEqual(response.resolver_match.func, is_mail_exists)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_is_mail_exists_missing_param(self):
        response = self.logged_client.get(reverse('is_mail_exists'), {}, HTTP_X_REQUESTED_WITH=self.xhr)

        self.assertEqual(response.resolver_match.func, is_mail_exists)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_is_mail_exists_param_very_long_mail(self):
        email = '{}@test.com'.format('test_email' * 200)
        response = self.logged_client.get(reverse('is_mail_exists'), {'email': email},
                                          HTTP_X_REQUESTED_WITH=self.xhr)

        self.assertEqual(response.resolver_match.func, is_mail_exists)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_is_mail_exists_param_missing_at_symbol(self):
        response = self.logged_client.get(reverse('is_mail_exists'), {'email': 'test_mail.com'},
                                          HTTP_X_REQUESTED_WITH=self.xhr)

        self.assertEqual(response.resolver_match.func, is_mail_exists)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_is_mail_exists_param_missing_dot_symbol(self):
        response = self.logged_client.get(reverse('is_mail_exists'), {'email': 'test_mail@coom'},
                                          HTTP_X_REQUESTED_WITH=self.xhr)

        self.assertEqual(response.resolver_match.func, is_mail_exists)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_is_mail_exists_param_not_allowed_symbols(self):
        response = self.logged_client.get(reverse('is_mail_exists'), {'email': 'test_m#$#@%ail@com.com'},
                                          HTTP_X_REQUESTED_WITH=self.xhr)

        self.assertEqual(response.resolver_match.func, is_mail_exists)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_is_mail_exists_successful_no_email_match(self):
        response = self.logged_client.get(reverse('is_mail_exists'), {'email': 'not_existing_mail@com.com'},
                                          HTTP_X_REQUESTED_WITH=self.xhr)
        response_data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.resolver_match.func, is_mail_exists)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, False)

    # ------------------------------------------------------------------------------------------------------------------
    def test_is_mail_exists_successful_email_match(self):
        response = self.logged_client.get(reverse('is_mail_exists'), {'email': 'index@user.com'},
                                          HTTP_X_REQUESTED_WITH=self.xhr)
        response_data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.resolver_match.func, is_mail_exists)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, True)

    # ------------------------------------------------------------------------------------------------------------------
    def test_sign_in_not_post_method(self):
        response = self.anonymous_client.get(reverse('sign_in'), {})

        self.assertEqual(response.resolver_match.func, sign_in)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_sign_in_missing_params(self):
        response = self.anonymous_client.post(reverse('sign_in'), {})

        self.assertEqual(response.resolver_match.func, sign_in)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_sign_in_invalid_username_param(self):
        response = self.anonymous_client.post(reverse('sign_in'),
                                              {'username': 'a', 'email': 'valid@email.com',
                                               'passw1': 'password', 'passw2': 'password'})
        self.assertEqual(response.resolver_match.func, sign_in)
        self.assertEqual(response.status_code, 400)

        response = self.anonymous_client.post(reverse('sign_in'),
                                              {'username': 'a' * 35, 'email': 'valid@email.com',
                                               'passw1': 'password', 'passw2': 'password'})
        self.assertEqual(response.resolver_match.func, sign_in)
        self.assertEqual(response.status_code, 400)

        response = self.anonymous_client.post(reverse('sign_in'),
                                              {'username': 'a#$(#*test_na', 'email': 'valid@email.com',
                                               'passw1': 'password', 'passw2': 'password'})
        self.assertEqual(response.resolver_match.func, sign_in)
        self.assertEqual(response.status_code, 400)

        response = self.anonymous_client.post(reverse('sign_in'),
                                              {'username': 'admin', 'email': 'valid@email.com',
                                               'passw1': 'password', 'passw2': 'password'})
        self.assertEqual(response.resolver_match.func, sign_in)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_sign_in_invalid_email_param(self):
        response = self.anonymous_client.post(reverse('sign_in'),
                                              {'username': 'valid_username', 'email': 'valid@email.com' * 50,
                                               'passw1': 'password', 'passw2': 'password'})
        self.assertEqual(response.resolver_match.func, sign_in)
        self.assertEqual(response.status_code, 400)

        response = self.anonymous_client.post(reverse('sign_in'),
                                              {'username': 'valid_username', 'email': 'no_at_symbol.com',
                                               'passw1': 'password', 'passw2': 'password'})
        self.assertEqual(response.resolver_match.func, sign_in)
        self.assertEqual(response.status_code, 400)

        response = self.anonymous_client.post(reverse('sign_in'),
                                              {'username': 'valid_username', 'email': 'no@dotcom',
                                               'passw1': 'password', 'passw2': 'password'})
        self.assertEqual(response.resolver_match.func, sign_in)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_sign_in_invalid_password_param(self):
        response = self.anonymous_client.post(reverse('sign_in'),
                                              {'username': 'valid_username', 'email': 'valid@email.com',
                                               'passw1': 'pass', 'passw2': 'pass'})  # Very short password
        self.assertEqual(response.resolver_match.func, sign_in)
        self.assertEqual(response.status_code, 400)

        response = self.anonymous_client.post(reverse('sign_in'),
                                              {'username': 'valid_username', 'email': 'valid@email.com',
                                               'passw1': 'pass' * 10, 'passw2': 'pass' * 10})  # Very long password
        self.assertEqual(response.resolver_match.func, sign_in)
        self.assertEqual(response.status_code, 400)

        response = self.anonymous_client.post(reverse('sign_in'),
                                              {'username': 'valid_username', 'email': 'valid@email.com',
                                               'passw1': 'password', 'passw2': 'not_matching_pass'})  # Not matching
        self.assertEqual(response.resolver_match.func, sign_in)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    @patch('app.views.index_views.validate_captcha', Mock(return_value=True))
    def test_sign_in_successful(self):
        response = self.anonymous_client.get(reverse('index'))
        self.assertEqual(response.resolver_match.func, index)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

        users_count = User.objects.all().count()
        response = self.anonymous_client.post(reverse('sign_in'),
                                              {'username': 'new_index_user', 'email': 'new_index@user.com',
                                               'passw1': 'password', 'passw2': 'password'})
        new_users = User.objects.all()

        self.assertEqual(response.resolver_match.func, sign_in)
        self.assertRedirects(response, reverse('index'), status_code=302, target_status_code=200)
        self.assertEqual(users_count + 1, new_users.count())
        self.assertTrue(new_users.filter(username='new_index_user').exists())

        response = self.anonymous_client.get(reverse('index'))
        self.assertEqual(response.resolver_match.func, index)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertEqual(len(response.context['books']), 0)
        self.assertFalse(len(response.context['recommend_books']))

    # ------------------------------------------------------------------------------------------------------------------
    @patch('app.views.index_views.restore_account', Mock())
    def test_restore_data_not_post(self):
        response = self.anonymous_client.get(reverse('restore_data'))

        self.assertEqual(response.resolver_match.func, restore_data)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    @patch('app.views.index_views.restore_account', Mock())
    def test_restore_data_missing_param(self):
        response = self.anonymous_client.post(reverse('restore_data'), {})

        self.assertEqual(response.resolver_match.func, restore_data)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    @patch('app.views.index_views.restore_account', Mock())
    def test_restore_data_not_valid_param(self):
        response = self.anonymous_client.post(reverse('restore_data'), {'email': 'valid@email.com' * 50})
        self.assertEqual(response.resolver_match.func, restore_data)
        self.assertEqual(response.status_code, 400)

        response = self.anonymous_client.post(reverse('restore_data'), {'email': 'no_at_symbol.com'})
        self.assertEqual(response.resolver_match.func, restore_data)
        self.assertEqual(response.status_code, 400)

        response = self.anonymous_client.post(reverse('restore_data'), {'email': 'no@dotcom'})
        self.assertEqual(response.resolver_match.func, restore_data)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    @patch('app.views.index_views.restore_account', Mock())
    def test_restore_data_not_existing_user(self):
        response = self.anonymous_client.post(reverse('restore_data'), {'email': 'valid_not_existing@email.com'})
        self.assertEqual(response.resolver_match.func, restore_data)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    @patch('app.views.index_views.restore_account', Mock())
    def test_restore_data_not_existing_user(self):
        response = self.anonymous_client.post(reverse('restore_data'), {'email': 'index@user.com'})
        response_data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.resolver_match.func, restore_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, True)
