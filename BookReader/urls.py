# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin

from app.views import index_views, additional_views, add_book_views, selected_book_views, library_views


urlpatterns = [
    url(r'^admin', include(admin.site.urls)),

    # Index urls.
    url(r'^$', index_views.index_view, name='index'),
    url(r'is-user-exists', index_views.is_user_exists_view),
    url(r'sign-in', index_views.sign_in_view),

    # Add book urls.
    url(r'^add-book', add_book_views.add_book_view),
    url(r'generate-authors', add_book_views.generate_authors_view),
    url(r'book-successful', add_book_views.add_book_successful_view),

    # Selected book urls.
    url(r'book/(?P<book_id>\d+)/$', selected_book_views.selected_book_view),
    url(r'home-add-book', selected_book_views.add_book_to_home_view),
    url(r'home-remove-book', selected_book_views.remove_book_from_home_view),
    url(r'change-rating', selected_book_views.change_rating_view),
    url(r'comment-add', selected_book_views.add_comment_view),

    # Library urls
    url(r'library', library_views.categories_view, name='categories'),
    url(r'^category/(?P<category_id>\d+)/$', library_views.selected_category_view),
    url(r'sort', library_views.sort_view),

    # Additional urls.
    url(r'thanks', additional_views.thanks_view),
    url(r'logout', additional_views.user_logout_view)
]
