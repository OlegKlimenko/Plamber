# -*- coding: utf-8 -*-

import random

from django.conf import settings

from ..models import TheUser

SHOW_REMINDER_COUNT = 150


# ----------------------------------------------------------------------------------------------------------------------
class ReminderMiddleware:
    """
    Middleware which handles the reminders behaviour. Adds special info in each request.
    Generates the status data used to raise reminders at the web part.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.STATIC_URL not in request.path and settings.MEDIA_URL not in request.path:
            self.set_reminder(request)
        else:
            request.session['reminder'] = None

        return self.get_response(request)

    def set_reminder(self, request):
        """
        Sets the reminder to request object.
        """
        if not request.user.is_anonymous:
            self.increment_counter(request)

            if request.session['reminder_counter'] >= SHOW_REMINDER_COUNT:
                request.session['reminder_counter'] = 0
                self.select_reminder(request)
            else:
                request.session['reminder'] = None

    def increment_counter(self, request):
        """
        Raises the reminder counter in each request.
        """
        if 'reminder_counter' in request.session:
            request.session['reminder_counter'] += 1
        else:
            request.session['reminder_counter'] = 0

    def select_reminder(self, request):
        user = TheUser.objects.get(id_user=request.user)

        all_user_reminders = user.get_web_reminders()

        if not all_user_reminders['disabled_all']:
            all_user_reminders.pop('disabled_all')
            possible_reminders = [key for key in all_user_reminders if all_user_reminders[key]]

            if possible_reminders:
                request.session['reminder'] = random.choice(possible_reminders)
            else:
                request.session['reminder'] = None
        else:
            request.session['reminder'] = None
