# -*- coding: utf-8 -*-

from django.contrib import auth
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.shortcuts import reverse

from ...models import TheUser
from ...views.reminder_views import update_reminder


# ----------------------------------------------------------------------------------------------------------------------
class ReminderViewsTest(TestCase):

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='logged_user', email='test@user.com', password='Dummy#password')
        cls.the_user = TheUser.objects.get(id_user=cls.user)

        cls.anonymous_client = Client()
        cls.logged_client = Client()
        cls.logged_client.login(username='logged_user', password='Dummy#password')

    # ------------------------------------------------------------------------------------------------------------------
    def test_update_reminder_not_logged(self):
        response = self.anonymous_client.post(reverse('update_reminder'), {})

        self.assertEqual(response.resolver_match.func, update_reminder)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_update_reminder_not_post(self):
        response = self.logged_client.get(reverse('update_reminder'))

        self.assertEqual(response.resolver_match.func, update_reminder)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_update_reminder_missing_params(self):
        response = self.logged_client.post(reverse('update_reminder'), {})

        self.assertEqual(response.resolver_match.func, update_reminder)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_update_reminder_invalid_params(self):
        response = self.logged_client.post(reverse('update_reminder'),
                                           {'field': 'extremely_long_field_name', 'value': True})

        self.assertEqual(response.resolver_match.func, update_reminder)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_update_update_reminder_not_existing_key(self):
        response = self.logged_client.post(reverse('update_reminder'), {'field': 'not_existing', 'value': True})
        user_reminders = TheUser.objects.get(id_user=self.user).get_web_reminders()

        self.assertEqual(response.resolver_match.func, update_reminder)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user_reminders['fb_page'], True)
        self.assertEqual(user_reminders['fb_group'], True)
        self.assertEqual(user_reminders['twitter'], True)
        self.assertEqual(user_reminders['vk'], True)
        self.assertEqual(user_reminders['app_download'], True)
        self.assertEqual(user_reminders['disabled_all'], False)

    # ------------------------------------------------------------------------------------------------------------------
    def test_update_update_reminder_existing_keys(self):
        response = self.logged_client.post(reverse('update_reminder'), {'field': 'fb_page'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func, update_reminder)

        response = self.logged_client.post(reverse('update_reminder'), {'field': 'app_download', 'value': False})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func, update_reminder)

        response = self.logged_client.post(reverse('update_reminder'), {'field': 'disabled_all', 'value': True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func, update_reminder)

        user_reminders = TheUser.objects.get(id_user=self.user).get_web_reminders()

        self.assertEqual(user_reminders['fb_page'], False)
        self.assertEqual(user_reminders['fb_group'], True)
        self.assertEqual(user_reminders['twitter'], True)
        self.assertEqual(user_reminders['vk'], True)
        self.assertEqual(user_reminders['app_download'], False)
        self.assertEqual(user_reminders['disabled_all'], True)
