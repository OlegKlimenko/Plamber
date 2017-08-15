# -*- coding: utf-8 -*-

from django.conf.urls import url

from .views import index_views

urlpatterns = [
    url('^user-login', index_views.user_login),
    url(r'send-mail', index_views.restore_data),
]
