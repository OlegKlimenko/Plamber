# -*- coding: utf-8 -*-

from django.shortcuts import reverse
from django.test import TestCase, Client

from ...models import Post, SupportMessage, Book
from ...views.about_views import about, send_message


# ----------------------------------------------------------------------------------------------------------------------
class AboutViewsTestCase(TestCase):

    # ------------------------------------------------------------------------------------------------------------------
    def setUp(self):
        self.client = Client()
        self.xhr = 'XMLHttpRequest'

    # ------------------------------------------------------------------------------------------------------------------
    def test_about(self):
        response_post = self.client.post(reverse('about'))
        self.assertEqual(response_post.resolver_match.func, about)
        self.assertEqual(response_post.status_code, 404)

        response_get = self.client.get(reverse('about'))
        self.assertEqual(response_post.resolver_match.func, about)
        self.assertEqual(response_get.status_code, 200)
        self.assertEqual(response_get.context['books_count'], Book.objects.all().count())
        self.assertEqual(response_get.context['posts'].count(), Post.objects.all().count())
        self.assertTemplateUsed(response_get, 'about.html')

    # ------------------------------------------------------------------------------------------------------------------
    def test_send_message_not_ajax(self):
        response = self.client.post(reverse('send_message'))
        self.assertEqual(response.resolver_match.func, send_message)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_send_message_missing_params(self):
        response = self.client.post(reverse('send_message'), HTTP_X_REQUESTED_WITH=self.xhr)
        self.assertEqual(response.resolver_match.func, send_message)
        self.assertEqual(response.status_code, 400)

        response = self.client.post(reverse('send_message'), {'email': 'test_email@mail.com'},
                                    HTTP_X_REQUESTED_WITH=self.xhr)
        self.assertEqual(response.resolver_match.func, send_message)
        self.assertEqual(response.status_code, 400)

        response = self.client.post(reverse('send_message'), {'text': 'Dummy Text'}, HTTP_X_REQUESTED_WITH=self.xhr)
        self.assertEqual(response.resolver_match.func, send_message)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_send_message_invalid_params(self):
        response = self.client.post(reverse('send_message'), {'text': 'Dummy' * 1500, 'email': 'missingAtSymbolEmail'},
                                    HTTP_X_REQUESTED_WITH=self.xhr)
        self.assertEqual(response.resolver_match.func, send_message)
        self.assertEqual(response.status_code, 400)

        response = self.client.post(reverse('send_message'), {'text': 'Correct text', 'email': 'missingext@mail'},
                                    HTTP_X_REQUESTED_WITH=self.xhr)
        self.assertEqual(response.resolver_match.func, send_message)
        self.assertEqual(response.status_code, 400)

        response = self.client.post(reverse('send_message'),
                                    {'text': 'Correct text', 'email': '{}@mail.com'.format('long_email' * 50)},
                                    HTTP_X_REQUESTED_WITH=self.xhr)
        self.assertEqual(response.resolver_match.func, send_message)
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------------------------------------------------------
    def test_send_message_success(self):
        messages_count = SupportMessage.objects.all().count()

        response = self.client.post(reverse('send_message'), {'text': 'Correct', 'email': 'correct@mail.com'},
                                    HTTP_X_REQUESTED_WITH=self.xhr)
        new_messages_count = SupportMessage.objects.all().count()

        self.assertEqual(response.resolver_match.func, send_message)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(new_messages_count, messages_count+1)

        response_content = str(response.content, encoding='utf-8')
        self.assertTrue(isinstance(response_content, str))
        self.assertEqual(response_content, 'true')
