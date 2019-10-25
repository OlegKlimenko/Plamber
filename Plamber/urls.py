# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin

from app.views import (index_views, additional_views, add_book_views, selected_book_views, library_views,
                       read_book_views, profile_views, about_views, reminder_views)


handler404 = 'app.views.error_views.not_found_404'
handler400 = 'app.views.error_views.bad_request_400'
handler403 = 'app.views.error_views.permission_denied_403'
handler500 = 'app.views.error_views.internal_error_500'

urlpatterns = [
    url(settings.ADMIN_URL, include(admin.site.urls)),

    # API urls
    url(r'^api/v1/', include('api.urls')),

    # Index urls.
    url(r'^$', index_views.index, name='index'),
    url(r'is-user-exists', index_views.is_user_exists, name='is_user_exists'),
    url(r'is-mail-exists', index_views.is_mail_exists, name='is_mail_exists'),
    url(r'sign-in', index_views.sign_in, name='sign_in'),
    url(r'send-mail', index_views.restore_data, name='restore_data'),

    # Read book urls.
    url(r'read-book/(?P<book_id>\d+)/$', read_book_views.open_book, name='read_book'),
    url(r'set-current-page', read_book_views.set_current_page, name='set_current_page'),

    # Add book urls.
    url(r'^add-book', add_book_views.add_book, name='add_book'),
    url(r'generate-authors', add_book_views.generate_authors, name='generate_authors'),
    url(r'generate-books', add_book_views.generate_books, name='generate_books'),
    url(r'book-successful', add_book_views.add_book_successful, name='book_successful'),

    # Selected book urls.
    url(r'book/(?P<book_id>\d+)/$', selected_book_views.selected_book, name='book'),
    url(r'store-book-image', selected_book_views.store_image, name='store_image'),
    url(r'home-add-book', selected_book_views.add_book_to_home, name='add_book_home_app'),
    url(r'home-remove-book', selected_book_views.remove_book_from_home),
    url(r'change-rating', selected_book_views.change_rating),
    url(r'comment-add', selected_book_views.add_comment),
    url(r'load-comments', selected_book_views.load_comments),
    url(r'report-book', selected_book_views.report_book, name='report-book'),

    # Library urls.
    url(r'library', library_views.all_categories, name='categories'),
    url(r'^category/(?P<category_id>\d+)/$', library_views.selected_category, name='category'),
    url(r'sort', library_views.sort),
    url(r'search-book', library_views.find_books),
    url(r'^author/(?P<author_id>\d+)/$', library_views.selected_author, name='author'),

    # Profile urls.
    url(r'profile/(?P<profile_id>\d+)/$', profile_views.profile, name='profile'),
    url(r'upload-avatar', profile_views.upload_avatar, name='upload_avatar'),
    url(r'change-password', profile_views.change_password, name='change_password'),

    # About project urls.
    url(r'about', about_views.about, name='about'),
    url(r'send-message', about_views.send_message, name='send_message'),

    # Additional urls.
    url(r'logout', additional_views.user_logout, name='logout'),
    url(r'unsubscribe/(?P<token>[0-9a-zA-Z_-]+)/', additional_views.unsubscribe, name='unsubscribe'),
    url(r'(?P<file>[%&+ \w]+.txt)', additional_views.share_txt, name='share_txt'),
    url(r'(?P<file>[%&+ \w]+.xml)', additional_views.share_xml, name='share_xml'),
    url(r'^update-reminder', reminder_views.update_reminder, name='update_reminder')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
