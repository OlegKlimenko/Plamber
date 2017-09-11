# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.conf import settings

from .views import index_views

# Remove in production when will define the way to get requests only from expected origin.
if settings.DEBUG:
    urlpatterns = [
        url('^user-login', index_views.user_login),
        url(r'send-mail', index_views.restore_data),
        url(r'is-user-exists', index_views.is_user_exists),
        url(r'is-mail-exists', index_views.is_mail_exists),
        url(r'sign-in', index_views.sign_in),
    ]

else:
    urlpatterns = []

