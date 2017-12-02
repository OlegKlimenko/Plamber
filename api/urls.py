# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.conf import settings

from .views import (index_views,
                    home_views,
                    library_views,
                    profile_views,
                    selected_book_views,
                    read_book_views,
                    upload_book_views)

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
        url(r'^home', home_views.home),
        url(r'recommend', home_views.recommendations),
        url(r'uploaded', home_views.uploaded_books),

        # Read book urls.
        url(r'read-book', read_book_views.open_book),
        url(r'set-current-page', read_book_views.set_current_page),

        # Add book urls.
        url(r'generate-authors', upload_book_views.generate_authors),
        url(r'generate-books', upload_book_views.generate_books),
        url(r'^upload-book', upload_book_views.upload_book),

        # Library urls.
        url(r'categories', library_views.all_categories),
        url(r'^category', library_views.selected_category, name='category_api'),
        url(r'search-book', library_views.find_book),

        # Selected book urls.
        url(r'^book', selected_book_views.selected_book, name='book_api'),
        url(r'^add-book-home', selected_book_views.add_book_to_home),
        url(r'^remove-book-home', selected_book_views.remove_book_from_home),
        url(r'change-rating', selected_book_views.change_rating),
        url(r'comment-add', selected_book_views.add_comment),

        # Profile urls.
        url(r'my-profile', profile_views.my_profile),
        url(r'change-password', profile_views.change_password),
        url(r'^upload-avatar', profile_views.upload_avatar),
    ]

else:
    urlpatterns = []
