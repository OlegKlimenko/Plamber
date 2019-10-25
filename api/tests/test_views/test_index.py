# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.test import TestCase

from rest_framework.test import APIClient

from ...views.index_views import user_login
from app.models import TheUser


# ----------------------------------------------------------------------------------------------------------------------
class IndexViewsTestCase(TestCase):

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='api_login', email='api_login@email.com', password='123456')
        cls.the_user = TheUser.objects.get(id_user=cls.user)

        cls.client = APIClient()
        cls.api_key = settings.API_SECRET_KEY

    # ------------------------------------------------------------------------------------------------------------------
    def test_user_login_missing_params(self):
        response = self.client.post(reverse('user_login_api'), {'app_key': self.api_key, 'username': 'username'})

        self.assertEqual(response.resolver_match.func, user_login)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], {'password': ['This field is required.']})

    # ------------------------------------------------------------------------------------------------------------------
    def test_user_login_too_long_username(self):
        response = self.client.post(reverse('user_login_api'), {'app_key': self.api_key,
                                                                'username': 'a' * 40,
                                                                'password': 'somepassword'})

        self.assertEqual(response.resolver_match.func, user_login)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], {'username': ['Ensure this field has no more than 30 characters.']})

    # ------------------------------------------------------------------------------------------------------------------
    def test_user_login_too_short_username(self):
        response = self.client.post(reverse('user_login_api'), {'app_key': self.api_key,
                                                                'username': 'a',
                                                                'password': 'somepassword'})

        self.assertEqual(response.resolver_match.func, user_login)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'],{'username': ['Ensure this field has at least 2 characters.']})

    # ------------------------------------------------------------------------------------------------------------------
    def test_user_login_username_regex_not_valid(self):
        username_patterns = [
            'ab#$@cdev', '#$@username', 'username%#&#&', 'db24!!!db34', '#$@234234', '#123dkf%'
        ]

        for pattern in username_patterns:
            with self.subTest(pattern=pattern):
                response = self.client.post(reverse('user_login_api'), {'app_key': self.api_key,
                                                                        'username': pattern,
                                                                        'password': 'somepassword'})

                self.assertEqual(response.resolver_match.func, user_login)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.data['detail'],
                                 {'username': ['This value does not match the required pattern.']})

    # ------------------------------------------------------------------------------------------------------------------
    def test_user_login_email_regex_not_valid(self):
        email_patterns = [
            'no_extension@ddd', '@first.missing', 'after_at_miss@', '$%#@474**.om', 'em#$@ail@m.com', '#em@ail@m.com'
        ]

        for pattern in email_patterns:
            with self.subTest(pattern=pattern):
                response = self.client.post(reverse('user_login_api'), {'app_key': self.api_key,
                                                                        'username': pattern,
                                                                        'password': 'somepassword'})

                self.assertEqual(response.resolver_match.func, user_login)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.data['detail'],
                                 {'username': ['This value does not match the required pattern.']})

    # ------------------------------------------------------------------------------------------------------------------
    def test_user_login_too_long_password(self):
        response = self.client.post(reverse('user_login_api'), {'app_key': self.api_key,
                                                                'username': 'test_username',
                                                                'password': 'p' * 17})

        self.assertEqual(response.resolver_match.func, user_login)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], {'password': ['Ensure this field has no more than 16 characters.']})

    # ------------------------------------------------------------------------------------------------------------------
    def test_user_login_valid_username_user_not_exists(self):
        response = self.client.post(reverse('user_login_api'), {'app_key': self.api_key,
                                                                'username': 'test_username',
                                                                'password': 'password'})

        self.assertEqual(response.resolver_match.func, user_login)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['data']['token'], None)
        self.assertEqual(response.data['detail'], 'not authenticated')

    # ------------------------------------------------------------------------------------------------------------------
    def test_user_login_valid_email_user_not_exists(self):
        response = self.client.post(reverse('user_login_api'), {'app_key': self.api_key,
                                                                'username': 'api_login_email@email.com',
                                                                'password': '123456'})

        self.assertEqual(response.resolver_match.func, user_login)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['data']['token'], None)
        self.assertEqual(response.data['detail'], 'not authenticated')

    # ------------------------------------------------------------------------------------------------------------------
    def test_user_login_success_with_username(self):
        response = self.client.post(reverse('user_login_api'), {'app_key': self.api_key,
                                                                'username': 'api_login',
                                                                'password': '123456'})

        self.assertEqual(response.resolver_match.func, user_login)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['token'], self.the_user.auth_token)
        self.assertEqual(response.data['detail'], 'successful')

    # ------------------------------------------------------------------------------------------------------------------
    def test_user_login_success_with_email(self):
        response = self.client.post(reverse('user_login_api'), {'app_key': self.api_key,
                                                                'username': 'api_login@email.com',
                                                                'password': '123456'})

        self.assertEqual(response.resolver_match.func, user_login)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['token'], self.the_user.auth_token)
        self.assertEqual(response.data['detail'], 'successful')
