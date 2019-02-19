# -*- coding: utf-8 -*-

import os
import shutil

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User, AnonymousUser
from django.shortcuts import reverse
from django.test import TestCase, Client

from ...models import TheUser
from ...views.additional_views import user_logout, share_txt, share_xml, unsubscribe

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(TEST_DIR, '../fixtures')

DESTINATION_DIR = os.path.join(settings.BASE_DIR, 'Plamber/additional/{}')


# ----------------------------------------------------------------------------------------------------------------------
class AdditionalViewsTest(TestCase):

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def setUpTestData(cls):
        shutil.copy(os.path.join(TEST_DATA_DIR, 'test.txt'), DESTINATION_DIR.format('test.txt'))
        shutil.copy(os.path.join(TEST_DATA_DIR, 'test.xml'), DESTINATION_DIR.format('test.xml'))

        cls.user = User.objects.create_user(username='additional', email='logout@user.com', password='Dummy#password')
        cls.user.date_joined = cls.user.date_joined.replace(microsecond=0)
        cls.user.save()

        cls.anonymous_client = Client()
        cls.logged_client = Client()
        cls.logged_client.login(username='additional', password='Dummy#password')

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def tearDownClass(cls):
        os.remove(DESTINATION_DIR.format('test.txt'))
        os.remove(DESTINATION_DIR.format('test.xml'))

    # ------------------------------------------------------------------------------------------------------------------
    def test_user_logout_not_post(self):
        response = self.logged_client.get(reverse('logout'))

        self.assertEqual(response.resolver_match.func, user_logout)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_user_logout_success(self):
        logged_user = auth.get_user(self.logged_client)

        self.assertEqual(logged_user, self.user)
        self.assertTrue(logged_user.is_authenticated())

        response = self.logged_client.post(reverse('logout'))
        logged_user = auth.get_user(self.logged_client)

        self.assertTrue(isinstance(logged_user, AnonymousUser))
        self.assertFalse(logged_user.is_authenticated())
        self.assertEqual(response.resolver_match.func, user_logout)
        self.assertRedirects(response, reverse('index'), status_code=302, target_status_code=200)

    # ------------------------------------------------------------------------------------------------------------------
    def test_share_txt_not_existing_file(self):
        response = self.logged_client.get(reverse('share_txt', kwargs={'file': 'not_existing.txt'}))

        self.assertEqual(response.resolver_match.func, share_txt)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_share_txt_existing_file(self):
        response = self.logged_client.get(reverse('share_txt', kwargs={'file': 'test.txt'}))
        response_data = response.content.decode('utf-8')

        self.assertEqual(response.resolver_match.func, share_txt)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, 'Test TXT data.')

    # ------------------------------------------------------------------------------------------------------------------
    def test_share_xml_not_existing_file(self):
        response = self.logged_client.get(reverse('share_xml', kwargs={'file': 'not_existing.xml'}))

        self.assertEqual(response.resolver_match.func, share_xml)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_share_xml_existing_file(self):
        response = self.logged_client.get(reverse('share_xml', kwargs={'file': 'test.xml'}))
        response_data = response.content.decode('utf-8')

        self.assertEqual(response.resolver_match.func, share_xml)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, '<note><body>Test XML data.</body></note>')

    # ------------------------------------------------------------------------------------------------------------------
    def test_unsubscribe_not_existing_date(self):
        self.assertTrue(TheUser.objects.get(id_user=self.user).subscription)
        user_token = '{}-{}'.format(self.user.username, 9379992)

        response = self.logged_client.get(reverse('unsubscribe', kwargs={'token': user_token}))

        self.assertEqual(response.resolver_match.func, unsubscribe)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(TheUser.objects.get(id_user=self.user).subscription)

    # ------------------------------------------------------------------------------------------------------------------
    def test_unsubscribe_not_existing_username(self):
        self.assertTrue(TheUser.objects.get(id_user=self.user).subscription)
        user_token = '{}-{}'.format('NOT_EXISTING_USERNAME', 9379992)

        response = self.logged_client.get(reverse('unsubscribe', kwargs={'token': user_token}))

        self.assertEqual(response.resolver_match.func, unsubscribe)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(TheUser.objects.get(id_user=self.user).subscription)

    # ------------------------------------------------------------------------------------------------------------------
    def test_unsubscribe_success(self):
        self.assertTrue(TheUser.objects.get(id_user=self.user).subscription)
        user_token = '{}-{}'.format(self.user.username, int(self.user.date_joined.timestamp()))

        response = self.logged_client.get(reverse('unsubscribe', kwargs={'token': user_token}))
        the_user = TheUser.objects.get(id_user=self.user)

        self.assertEqual(response.resolver_match.func, unsubscribe)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(the_user.subscription)
        self.assertTemplateUsed(response, 'additional/unsubscribe.html')
        self.assertEqual(response.context['user'], the_user)
