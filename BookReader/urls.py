# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin

from app.views import (index_views, additional_views, add_book_views, selected_book_views, library_views,
                       read_book_views)


urlpatterns = [
    url(r'^not/an/admin/url/', include(admin.site.urls)),

    # Index urls.
    url(r'^$', index_views.index_view, name='index'),
    url(r'is-user-exists', index_views.is_user_exists_view),
    url(r'sign-in', index_views.sign_in_view),

    # Read book urls.
    url(r'read-book/(?P<book_id>\d+)/$', read_book_views.open_book_view),
    url(r'set-current-page', read_book_views.set_current_page_view),

    # Add book urls.
    url(r'^add-book', add_book_views.add_book_view, name='add_book'),
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
    url(r'search-book', library_views.find_books),

    # Additional urls.
    url(r'thanks', additional_views.thanks_view),
    url(r'logout', additional_views.user_logout_view)

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
