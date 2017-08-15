# -*- coding: utf-8 -*-

from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'app'

    def ready(self):
        import app.signals