# -*- coding: utf-8 -*-

import os
from http.cookies import SimpleCookie

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from django.test import TestCase, Client

from ...models import TheUser, Book, AddedBook, Category, Language, Author
from ...views.read_book_views import open_book, set_current_page

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(TEST_DIR, '../fixtures')


# ----------------------------------------------------------------------------------------------------------------------
class ReadBookViewsTest(TestCase):

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def setUpTestData(cls):
        cls.xhr = 'XMLHttpRequest'
        cls.user = User.objects.create_user(username='read_book_user', email='read_book@user.com',
                                            password='Dummy#password')
        cls.the_user = TheUser.objects.get(id_user=cls.user)

        cls.category = Category.objects.create(category_name='Category_name')
        cls.language = Language.objects.create(language='English')
        cls.author = Author.objects.create(author_name='Author_name')

        cls.anonymous_client = Client()
        cls.logged_client = Client()
        cls.logged_client.login(username='read_book_user', password='Dummy#password')

        cls.generate_books()
        cls.added_book = AddedBook.objects.create(id_user=cls.the_user, id_book=cls.book)

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def generate_books(cls):
        test_book_path = os.path.join(TEST_DATA_DIR, 'test_book.pdf')

        cls.book = Book.objects.create(
            book_name='Added_book_test',
            id_author=cls.author,
            id_category=cls.category,
            language=cls.language,
            book_file=SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
            who_added=cls.the_user
        )
        cls.not_added_book = Book.objects.create(
            book_name='not_added_book',
            id_author=cls.author,
            id_category=cls.category,
            language=cls.language,
            book_file=SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
            who_added=cls.the_user
        )

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def tearDownClass(cls):
        for book in Book.objects.all():
            if os.path.exists(book.book_file.path):
                os.remove(book.book_file.path)
            if book.photo and os.path.exists(book.photo.path):
                os.remove(book.photo.path)

    # ------------------------------------------------------------------------------------------------------------------
    def test_open_book_anonymous_success_no_cookies(self):
        self.anonymous_client.cookies.pop('plamber_book_{}'.format(self.book.id), None)
        response = self.anonymous_client.get(reverse('read_book', kwargs={'book_id': self.book.id}))

        self.assertEqual(response.resolver_match.func, open_book)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['book_page'], 1)
        self.assertEqual(response.context['book'], self.book)

    # ------------------------------------------------------------------------------------------------------------------
    def test_open_book_anonymous_success_with_cookie(self):
        self.anonymous_client.cookies = SimpleCookie({'plamber_book_{}'.format(self.book.id): 666})
        response = self.anonymous_client.get(reverse('read_book', kwargs={'book_id': self.book.id}))

        self.assertEqual(response.resolver_match.func, open_book)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['book_page'], 666)
        self.assertEqual(response.context['book'], self.book)

    # ------------------------------------------------------------------------------------------------------------------
    def test_open_book_anonymous_success_not_valid_cookie_type(self):
        self.anonymous_client.cookies = SimpleCookie({'plamber_book_{}'.format(self.book.id): 'string'})
        response = self.anonymous_client.get(reverse('read_book', kwargs={'book_id': self.book.id}))

        self.assertEqual(response.resolver_match.func, open_book)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['book_page'], 1)
        self.assertEqual(response.context['book'], self.book)

    # ------------------------------------------------------------------------------------------------------------------
    def test_open_book_anonymous_success_other_book_cookie(self):
        self.anonymous_client.cookies = SimpleCookie({'plamber_book_10000': '60'})
        response = self.anonymous_client.get(reverse('read_book', kwargs={'book_id': self.book.id}))

        self.assertEqual(response.resolver_match.func, open_book)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['book_page'], 1)
        self.assertEqual(response.context['book'], self.book)

    # ------------------------------------------------------------------------------------------------------------------
    def test_open_book_anonymous_private_book(self):
        self.book.private_book = True
        self.book.save()

        response = self.anonymous_client.get(reverse('read_book', kwargs={'book_id': self.book.id}))
        self.assertEqual(response.resolver_match.func, open_book)
        self.assertEqual(response.status_code, 404)

        self.book.private_book = False
        self.book.save()

    # ------------------------------------------------------------------------------------------------------------------
    def test_open_book_anonymous_blocked_book(self):
        self.book.blocked_book = True
        self.book.save()

        response = self.anonymous_client.get(reverse('read_book', kwargs={'book_id': self.book.id}))
        self.assertEqual(response.resolver_match.func, open_book)
        self.assertRedirects(response, reverse('book', kwargs={'book_id': self.book.id}),
                             status_code=302, target_status_code=200)

        self.book.blocked_book = False
        self.book.save()

    # ------------------------------------------------------------------------------------------------------------------
    def test_open_book_book_not_exist(self):
        response = self.logged_client.get(reverse('read_book', kwargs={'book_id': self.book.id * 100}))

        self.assertEqual(response.resolver_match.func, open_book)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_open_book_not_added_to_reading(self):
        response = self.logged_client.get(reverse('read_book', kwargs={'book_id': self.not_added_book.id}))

        self.assertEqual(response.resolver_match.func, open_book)
        self.assertRedirects(response, reverse('book', kwargs={'book_id': self.not_added_book.id}),
                             status_code=302, target_status_code=200)

    # ------------------------------------------------------------------------------------------------------------------
    def test_open_book_not_added_to_reading_private_book(self):
        self.not_added_book.private_book = True
        self.not_added_book.save()

        response = self.logged_client.get(reverse('read_book', kwargs={'book_id': self.not_added_book.id}))
        self.assertEqual(response.resolver_match.func, open_book)
        self.assertRedirects(response, reverse('book', kwargs={'book_id': self.not_added_book.id}),
                             status_code=302, target_status_code=200)

        self.not_added_book.private_book = False
        self.not_added_book.save()

    # ------------------------------------------------------------------------------------------------------------------
    def test_open_book_not_added_to_reading_blocked_book(self):
        self.not_added_book.blocked_book = True
        self.not_added_book.save()

        response = self.logged_client.get(reverse('read_book', kwargs={'book_id': self.not_added_book.id}))
        self.assertEqual(response.resolver_match.func, open_book)
        self.assertRedirects(response, reverse('book', kwargs={'book_id': self.not_added_book.id}),
                             status_code=302, target_status_code=200)

        self.not_added_book.blocked_book = False
        self.not_added_book.save()

    # ------------------------------------------------------------------------------------------------------------------
    def test_open_book_last_read_date_change(self):
        response = self.logged_client.get(reverse('read_book', kwargs={'book_id': self.book.id}))
        last_read_date = AddedBook.objects.get(id=self.added_book.id).last_read

        self.assertEqual(response.resolver_match.func, open_book)
        self.assertEqual(response.status_code, 200)

        response = self.logged_client.get(reverse('read_book', kwargs={'book_id': self.book.id}))
        new_last_read = AddedBook.objects.get(id=self.added_book.id).last_read

        self.assertEqual(response.resolver_match.func, open_book)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(new_last_read, last_read_date)
        self.assertTrue(new_last_read > last_read_date)

    # ------------------------------------------------------------------------------------------------------------------
    def test_open_book_success(self):
        response = self.logged_client.get(reverse('read_book', kwargs={'book_id': self.book.id}))

        self.assertEqual(response.resolver_match.func, open_book)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'read_book.html')
        self.assertEqual(response.context['book'], self.book)
        self.assertEqual(response.context['book_page'], self.added_book.last_page)

    # ------------------------------------------------------------------------------------------------------------------
    def test_open_book_success_private_book(self):
        self.book.private_book = True
        self.book.save()

        response = self.logged_client.get(reverse('read_book', kwargs={'book_id': self.book.id}))
        self.assertEqual(response.resolver_match.func, open_book)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'read_book.html')
        self.assertEqual(response.context['book'], self.book)
        self.assertEqual(response.context['book_page'], self.added_book.last_page)

        self.book.private_book = False
        self.book.save()

    # ------------------------------------------------------------------------------------------------------------------
    def test_open_book_success_blocked_book(self):
        self.book.blocked_book = True
        self.book.save()

        response = self.logged_client.get(reverse('read_book', kwargs={'book_id': self.book.id}))
        self.assertEqual(response.resolver_match.func, open_book)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'read_book.html')
        self.assertEqual(response.context['book'], self.book)
        self.assertEqual(response.context['book_page'], self.added_book.last_page)

        self.book.blocked_book = False
        self.book.save()

    # ------------------------------------------------------------------------------------------------------------------
    def test_set_current_page_not_ajax(self):
        response = self.logged_client.post(reverse('set_current_page'))

        self.assertEqual(response.resolver_match.func, set_current_page)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_set_current_page_missing_params(self):
        response = self.logged_client.post(reverse('set_current_page'), {},
                                           HTTP_X_REQUESTED_WITH=self.xhr)

        self.assertEqual(response.resolver_match.func, set_current_page)
        self.assertEqual(response.status_code, 404)

        response = self.logged_client.post(reverse('set_current_page'), {'page': 13},
                                           HTTP_X_REQUESTED_WITH=self.xhr)

        self.assertEqual(response.resolver_match.func, set_current_page)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_set_current_page_invalid_page_param(self):
        response = self.logged_client.post(reverse('set_current_page'), {'page': 0, 'book': self.book.id},
                                           HTTP_X_REQUESTED_WITH=self.xhr)
        self.assertEqual(response.resolver_match.func, set_current_page)
        self.assertEqual(response.status_code, 404)

        response = self.logged_client.post(reverse('set_current_page'), {'page': -1, 'book': self.book.id},
                                           HTTP_X_REQUESTED_WITH=self.xhr)
        self.assertEqual(response.resolver_match.func, set_current_page)
        self.assertEqual(response.status_code, 404)

        response = self.logged_client.post(reverse('set_current_page'), {'page': 'NAN', 'book': self.book.id},
                                           HTTP_X_REQUESTED_WITH=self.xhr)
        self.assertEqual(response.resolver_match.func, set_current_page)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_set_current_page_invalid_book_param(self):
        response = self.logged_client.post(reverse('set_current_page'), {'page': 12, 'book': str(self.book.id) * 500},
                                           HTTP_X_REQUESTED_WITH=self.xhr)
        self.assertEqual(response.resolver_match.func, set_current_page)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_set_current_page_success(self):
        response = self.logged_client.post(reverse('set_current_page'), {'page': 14, 'book': self.book.id},
                                           HTTP_X_REQUESTED_WITH=self.xhr)
        page = AddedBook.objects.get(id_user=self.the_user, id_book=self.book).last_page
        self.assertEqual(response.resolver_match.func, set_current_page)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(page, 14)

        response = self.logged_client.post(reverse('set_current_page'), {'page': 300, 'book': self.book.id},
                                           HTTP_X_REQUESTED_WITH=self.xhr)
        page = AddedBook.objects.get(id_user=self.the_user, id_book=self.book).last_page
        self.assertEqual(response.resolver_match.func, set_current_page)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(page, 300)
