# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.conf import settings

from .views import index_views, home_views, library_views, profile_views

# Remove in production when will define the way to get requests only from expected origin.
if settings.DEBUG:
    urlpatterns = [
        # Start page urls.
        url('^user-login', index_views.user_login),
        url(r'send-mail', index_views.restore_data),
        url(r'is-user-exists', index_views.is_user_exists),
        url(r'is-mail-exists', index_views.is_mail_exists),
        url(r'sign-in', index_views.sign_in),

        # Home urls.
        url(r'home', home_views.home),
        url(r'recommend', home_views.recommendations),

        # Library urls.
        url(r'categories', library_views.all_categories),
        url(r'^category/(?P<category_id>\d+)/$', library_views.selected_category, name='category_api'),

        # Profile urls.
        url(r'my-profile', profile_views.my_profile),
        url(r'change-password', profile_views.change_password),
        url(r'upload-avatar', profile_views.upload_avatar),
    ]

else:
    urlpatterns = []

