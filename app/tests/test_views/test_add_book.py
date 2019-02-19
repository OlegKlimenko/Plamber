# -*- coding: utf-8 -*-

import json
import os

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.shortcuts import reverse

from ...models import Category, Language, Author, TheUser, Book, AddedBook
from ...views.add_book_views import add_book, generate_authors, generate_books, add_book_successful

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(TEST_DIR, '../fixtures')


# ----------------------------------------------------------------------------------------------------------------------
class AddBookViewsTest(TestCase):

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def setUpTestData(cls):
        cls.xhr = 'XMLHttpRequest'
        cls.user = User.objects.create(username='test_user1')
        cls.the_user = TheUser.objects.get(id_user=cls.user)
        cls.user.set_password('Dummy#password')
        cls.user.save()

        cls.category1 = Category.objects.create(category_name='last category')
        cls.category2 = Category.objects.create(category_name='a first category')
        cls.language_en = Language.objects.create(language='English')
        cls.language_ru = Language.objects.create(language='Russian')

        cls.author1 = Author.objects.create(author_name='New Author Name')
        cls.author2 = Author.objects.create(author_name='A best one')
        cls.author3 = Author.objects.create(author_name='The new author')

        cls.anonymous_client = Client()
        cls.logged_client = Client()
        cls.logged_client.login(username='test_user1', password='Dummy#password')

        cls.generate_books()

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def generate_books(cls):
        test_book_path = os.path.join(TEST_DATA_DIR, 'test_book.pdf')

        for book_name in ['First Book', 'Second Book', 'Third Book']:
            Book.objects.create(
                book_name=book_name,
                id_author=cls.author1,
                id_category=cls.category1,
                language=cls.language_en,
                book_file=SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
                who_added=cls.the_user
            )

    # ------------------------------------------------------------------------------------------------------------------
    def tearDown(self):
        for book in Book.objects.all():
            if os.path.exists(book.book_file.path):
                os.remove(book.book_file.path)
            if book.photo and os.path.exists(book.photo.path):
                os.remove(book.photo.path)

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_book_not_logged_user(self):
        response = self.anonymous_client.get(reverse('add_book'))

        self.assertEqual(response.resolver_match.func, add_book)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'), status_code=302, target_status_code=200)

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_book_logged_user(self):
        response = self.logged_client.get(reverse('add_book'))

        all_categories = Category.objects.all()
        all_languages = Language.objects.all()

        self.assertEqual(response.resolver_match.func, add_book)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_book.html')
        self.assertEqual(response.context['categories'].count(), all_categories.count())
        self.assertEqual(response.context['categories'][0], self.category2)
        self.assertEqual(response.context['languages'].count(), all_languages.count())

    # ------------------------------------------------------------------------------------------------------------------
    def test_generate_authors_not_ajax(self):
        response = self.logged_client.get(reverse('generate_authors'))

        self.assertEqual(response.resolver_match.func, generate_authors)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_generate_authors_missing_params(self):
        response = self.logged_client.get(reverse('generate_authors'), {}, HTTP_X_REQUESTED_WITH=self.xhr)

        self.assertEqual(response.resolver_match.func, generate_authors)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_generate_authors_invalid_params(self):
        response = self.logged_client.get(reverse('generate_authors'), {'part': ''}, HTTP_X_REQUESTED_WITH=self.xhr)

        self.assertEqual(response.resolver_match.func, generate_authors)
        self.assertEqual(response.status_code, 404)

        response = self.logged_client.get(reverse('generate_authors'), {'part': 'x' * 75},
                                          HTTP_X_REQUESTED_WITH=self.xhr)

        self.assertEqual(response.resolver_match.func, generate_authors)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_generate_authors_success_parts(self):
        response = self.logged_client.get(reverse('generate_authors'), {'part': 'the'}, HTTP_X_REQUESTED_WITH=self.xhr)
        response_content = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.resolver_match.func, generate_authors)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response_content, list))
        self.assertEqual(len(response_content), 1)
        self.assertEqual(response_content, ['The new author'])

        response = self.logged_client.get(reverse('generate_authors'), {'part': 'new'}, HTTP_X_REQUESTED_WITH=self.xhr)
        response_content = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.resolver_match.func, generate_authors)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response_content, list))
        self.assertEqual(len(response_content), 2)
        self.assertEqual(response_content, ['New Author Name', 'The new author'])

        response = self.logged_client.get(reverse('generate_authors'), {'part': 'e'}, HTTP_X_REQUESTED_WITH=self.xhr)
        response_content = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.resolver_match.func, generate_authors)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response_content, list))
        self.assertEqual(len(response_content), 3)
        self.assertEqual(response_content, ['New Author Name', 'A best one', 'The new author'])

    # ------------------------------------------------------------------------------------------------------------------
    def test_generate_authors_success_full_name(self):
        response = self.logged_client.get(reverse('generate_authors'), {'part': 'New Author Name'},
                                          HTTP_X_REQUESTED_WITH=self.xhr)
        response_content = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.resolver_match.func, generate_authors)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response_content, list))
        self.assertEqual(len(response_content), 1)
        self.assertEqual(response_content, ['New Author Name'])

        response = self.logged_client.get(reverse('generate_authors'), {'part': 'A best one'},
                                          HTTP_X_REQUESTED_WITH=self.xhr)
        response_content = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.resolver_match.func, generate_authors)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response_content, list))
        self.assertEqual(len(response_content), 1)
        self.assertEqual(response_content, ['A best one'])

    # ------------------------------------------------------------------------------------------------------------------
    def test_generate_authors_success_different_case(self):
        response = self.logged_client.get(reverse('generate_authors'), {'part': 'AUTHOR'},
                                          HTTP_X_REQUESTED_WITH=self.xhr)
        response_content = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.resolver_match.func, generate_authors)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response_content, list))
        self.assertEqual(len(response_content), 2)
        self.assertEqual(response_content, ['New Author Name', 'The new author'])

        response = self.logged_client.get(reverse('generate_authors'), {'part': 'author'},
                                          HTTP_X_REQUESTED_WITH=self.xhr)
        response_content = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.resolver_match.func, generate_authors)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response_content, list))
        self.assertEqual(len(response_content), 2)
        self.assertEqual(response_content, ['New Author Name', 'The new author'])

        response = self.logged_client.get(reverse('generate_authors'), {'part': 'aUthOR'},
                                          HTTP_X_REQUESTED_WITH=self.xhr)
        response_content = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.resolver_match.func, generate_authors)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response_content, list))
        self.assertEqual(len(response_content), 2)
        self.assertEqual(response_content, ['New Author Name', 'The new author'])

    # ------------------------------------------------------------------------------------------------------------------
    def test_generate_books_not_ajax(self):
        response = self.logged_client.get(reverse('generate_books'))

        self.assertEqual(response.resolver_match.func, generate_books)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_generate_books_missing_params(self):
        response = self.logged_client.get(reverse('generate_books'), {}, HTTP_X_REQUESTED_WITH=self.xhr)

        self.assertEqual(response.resolver_match.func, generate_books)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_generate_books_invalid_params(self):
        response = self.logged_client.get(reverse('generate_books'), {'part': ''}, HTTP_X_REQUESTED_WITH=self.xhr)

        self.assertEqual(response.resolver_match.func, generate_books)
        self.assertEqual(response.status_code, 404)

        response = self.logged_client.get(reverse('generate_books'), {'part': 'y' * 170},
                                          HTTP_X_REQUESTED_WITH=self.xhr)

        self.assertEqual(response.resolver_match.func, generate_books)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_generate_books_success_parts(self):
        response = self.logged_client.get(reverse('generate_books'), {'part': 'book'},
                                          HTTP_X_REQUESTED_WITH=self.xhr)
        response_content = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.resolver_match.func, generate_books)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response_content, list))
        self.assertEqual(len(response_content), 3)
        self.assertTrue(response_content[0].get('name', False))
        self.assertTrue(response_content[0].get('url', False))
        self.assertEqual(response_content[0]['name'], 'First Book')
        self.assertEqual(response_content[0]['url'], '/book/{}/'.format(Book.objects.get(book_name='First Book').id))

        response = self.logged_client.get(reverse('generate_books'), {'part': 'i'},
                                          HTTP_X_REQUESTED_WITH=self.xhr)
        response_content = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.resolver_match.func, generate_books)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response_content, list))
        self.assertEqual(len(response_content), 2)
        self.assertTrue(response_content[1].get('name', False))
        self.assertTrue(response_content[1].get('url', False))
        self.assertEqual(response_content[1]['name'], 'Third Book')
        self.assertEqual(response_content[1]['url'], '/book/{}/'.format(Book.objects.get(book_name='Third Book').id))

    # ------------------------------------------------------------------------------------------------------------------
    def test_generate_books_success_full_name(self):
        response = self.logged_client.get(reverse('generate_books'), {'part': 'Second Book'},
                                          HTTP_X_REQUESTED_WITH=self.xhr)
        response_content = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.resolver_match.func, generate_books)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response_content, list))
        self.assertEqual(len(response_content), 1)
        self.assertTrue(response_content[0].get('name', False))
        self.assertTrue(response_content[0].get('url', False))
        self.assertEqual(response_content[0]['name'], 'Second Book')
        self.assertEqual(response_content[0]['url'], '/book/{}/'.format(Book.objects.get(book_name='Second Book').id))

    # ------------------------------------------------------------------------------------------------------------------
    def test_generate_books_success_different_case(self):
        response = self.logged_client.get(reverse('generate_books'), {'part': 'second book'},
                                          HTTP_X_REQUESTED_WITH=self.xhr)
        response_content = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.resolver_match.func, generate_books)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response_content, list))
        self.assertEqual(len(response_content), 1)
        self.assertTrue(response_content[0].get('name', False))
        self.assertTrue(response_content[0].get('url', False))
        self.assertEqual(response_content[0]['name'], 'Second Book')
        self.assertEqual(response_content[0]['url'], '/book/{}/'.format(Book.objects.get(book_name='Second Book').id))

        response = self.logged_client.get(reverse('generate_books'), {'part': 'SECOND BOOK'},
                                          HTTP_X_REQUESTED_WITH=self.xhr)
        response_content = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.resolver_match.func, generate_books)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response_content, list))
        self.assertEqual(len(response_content), 1)
        self.assertTrue(response_content[0].get('name', False))
        self.assertTrue(response_content[0].get('url', False))
        self.assertEqual(response_content[0]['name'], 'Second Book')
        self.assertEqual(response_content[0]['url'], '/book/{}/'.format(Book.objects.get(book_name='Second Book').id))

        response = self.logged_client.get(reverse('generate_books'), {'part': 'seCoND bOOk'},
                                          HTTP_X_REQUESTED_WITH=self.xhr)
        response_content = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.resolver_match.func, generate_books)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response_content, list))
        self.assertEqual(len(response_content), 1)
        self.assertTrue(response_content[0].get('name', False))
        self.assertTrue(response_content[0].get('url', False))
        self.assertEqual(response_content[0]['name'], 'Second Book')
        self.assertEqual(response_content[0]['url'], '/book/{}/'.format(Book.objects.get(book_name='Second Book').id))

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_book_successful_not_post(self):
        response = self.logged_client.get(reverse('book_successful'))

        self.assertEqual(response.resolver_match.func, add_book_successful)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_book_successful_missing_all_params(self):
        response = self.logged_client.post(reverse('book_successful'), {})

        self.assertEqual(response.resolver_match.func, add_book_successful)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_book_successful_missing_some_params(self):
        response = self.logged_client.post(
            reverse('book_successful'), {'book_name': 'Extra new book', 'author': 'A. Pushkin', 'about': 'blah blah'}
        )

        self.assertEqual(response.resolver_match.func, add_book_successful)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_book_successful_invalid_params(self):
        test_book_path = os.path.join(TEST_DATA_DIR, 'test_book.pdf')

        response = self.logged_client.post(
            reverse('book_successful'),
            {
                'bookname': 'new_name' * 100,
                'author': 'new_author' * 100,
                'category': 'a' * 35,
                'language': 'l' * 35,
                'about': 'Some text about book',
                'bookfile': SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read())
            }
        )

        self.assertEqual(response.resolver_match.func, add_book_successful)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_book_successful_invalid_book_type(self):
        test_book_path = os.path.join(TEST_DATA_DIR, 'test_book_image.png')

        response = self.logged_client.post(
            reverse('book_successful'),
            {
                'bookname': 'new_name',
                'author': 'new_author',
                'category': 'a first category',
                'language': 'English',
                'about': 'Some text about book',
                'bookfile': SimpleUploadedFile('test_book_image.png', open(test_book_path, 'rb').read())
            }
        )

        self.assertEqual(response.resolver_match.func, add_book_successful)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_book_successful_with_creating_new_author(self):
        test_book_path = os.path.join(TEST_DATA_DIR, 'test_book.pdf')

        books_count = Book.objects.all().count()
        authors_count = Author.objects.all().count()
        added_book_count = AddedBook.objects.all().count()

        response = self.logged_client.post(
            reverse('book_successful'),
            {
                'bookname': 'book_with_new_author',
                'author': 'new_author_for_book',
                'category': 'a first category',
                'language': 'English',
                'about': 'Some text about book',
                'bookfile': SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read())
            }
        )
        response_content = response.content.decode('utf-8')
        created_book = Book.objects.get(book_name='book_with_new_author')

        self.assertEqual(response.resolver_match.func, add_book_successful)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_content, reverse('book', kwargs={'book_id': created_book.id}))
        self.assertEqual(Book.objects.all().count(), books_count+1)
        self.assertEqual(Author.objects.all().count(), authors_count+1)
        self.assertEqual(AddedBook.objects.all().count(), added_book_count+1)
        self.assertTrue(Author.objects.filter(author_name='new_author_for_book').exists())
        self.assertTrue(Book.objects.filter(book_name='book_with_new_author').exists())
        self.assertEqual(Book.objects.filter(book_name='book_with_new_author').count(), 1)

    # ------------------------------------------------------------------------------------------------------------------
    def test_add_book_successful_existing_author(self):
        test_book_path = os.path.join(TEST_DATA_DIR, 'test_book.pdf')

        books_count = Book.objects.all().count()
        authors_count = Author.objects.all().count()
        added_book_count = AddedBook.objects.all().count()

        response = self.logged_client.post(
            reverse('book_successful'),
            {
                'bookname': 'book_existing_author',
                'author': 'A best one',
                'category': 'a first category',
                'language': 'English',
                'about': 'Some text about book',
                'bookfile': SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read())
            }
        )
        response_content = response.content.decode('utf-8')
        created_book = Book.objects.get(book_name='book_existing_author')

        self.assertEqual(response.resolver_match.func, add_book_successful)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_content, reverse('book', kwargs={'book_id': created_book.id}))
        self.assertEqual(Book.objects.all().count(), books_count+1)
        self.assertEqual(Author.objects.all().count(), authors_count)
        self.assertEqual(AddedBook.objects.all().count(), added_book_count + 1)
        self.assertTrue(Book.objects.filter(book_name='book_existing_author').exists())
        self.assertEqual(Book.objects.filter(book_name='book_existing_author').count(), 1)
