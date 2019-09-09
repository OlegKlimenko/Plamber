# -*- coding: utf-8 -*-

import os

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from django.test import TestCase, Client

from ...models import Author, Book, AddedBook, Category, Language, TheUser
from ...views.library_views import all_categories, selected_category, selected_author

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(TEST_DIR, '../fixtures')

NOT_EXISTS_CATEGORY = 10000

# ----------------------------------------------------------------------------------------------------------------------
class LibraryViewsTestCase(TestCase):

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def setUpTestData(cls):
        test_book_path = os.path.join(TEST_DATA_DIR, 'test_book.pdf')

        cls.xhr = 'XMLHttpRequest'
        cls.user = User.objects.create_user(username='libusername', email='lib@user.com', password='password')
        cls.the_user = TheUser.objects.get(id_user=cls.user)

        cls.anonymous_client = Client()
        cls.logged_client = Client()
        cls.logged_client.login(username='libusername', password='password')

        cls.category = Category.objects.create(category_name='CustomCategoryName')
        cls.language = Language.objects.create(language='French')
        cls.author1 = Author.objects.create(author_name='SomeAuthorCategoryName')
        cls.author2 = Author.objects.create(author_name='SomeOtherCategoryNameAuthor')

        cls.book1 = Book.objects.create(
            book_name='category_book_test1',
            id_author=cls.author1,
            id_category=cls.category,
            language=cls.language,
            book_file=SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
            who_added=cls.the_user
        )
        cls.book2 = Book.objects.create(
            book_name='category_book_test2',
            id_author=cls.author2,
            id_category=cls.category,
            language=cls.language,
            book_file=SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
            who_added=cls.the_user
        )

        AddedBook.objects.create(id_user=cls.the_user, id_book=cls.book1)
        AddedBook.objects.create(id_user=cls.the_user, id_book=cls.book2)

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def tearDownClass(cls):
        for book in Book.objects.all():
            if os.path.exists(book.book_file.path):
                os.remove(book.book_file.path)
            if book.photo and os.path.exists(book.photo.path):
                os.remove(book.photo.path)

    # ------------------------------------------------------------------------------------------------------------------
    def test_all_categories_invalid_request_method(self):
        response = self.anonymous_client.post(reverse('categories'))

        self.assertEqual(response.resolver_match.func, all_categories)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_all_categories(self):
        response = self.anonymous_client.get(reverse('categories'))

        self.assertEqual(response.resolver_match.func, all_categories)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'categories.html')
        self.assertIn('categories', response.context)
        self.assertIn('most_readable_books', response.context)
        self.assertIn('books_count', response.context)
        self.assertEqual(len(response.context['categories']), Category.objects.all().count())
        # self.assertEqual('') TODO: Add this test to most readable books
        self.assertEqual(response.context['books_count'], Book.objects.all().count())

    # ------------------------------------------------------------------------------------------------------------------
    def test_selected_category_invalid_request_method(self):
        response = self.anonymous_client.post(reverse('category', kwargs={'category_id': 10000}))

        self.assertEqual(response.resolver_match.func, selected_category)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_selected_category_not_exists(self):
        response = self.anonymous_client.get(reverse('category', kwargs={'category_id': 10000}))

        self.assertEqual(response.resolver_match.func, selected_category)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_selected_category(self):
        response = self.anonymous_client.get(reverse('category', kwargs={'category_id': self.category.id}))

        self.assertEqual(response.resolver_match.func, selected_category)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'selected_category.html')
        self.assertIn('category', response.context)
        self.assertIn('books', response.context)
        self.assertIn('category_number', response.context)
        self.assertEqual(response.context['category'].category_name, 'CustomCategoryName')
        self.assertEqual(len(response.context['books']), Book.objects.filter(id_category=self.category).count())
        self.assertEqual(list(response.context['books']), list(Book.objects.filter(id_category=self.category)))
        self.assertEqual(int(response.context['category_number']), self.category.id)

    # ------------------------------------------------------------------------------------------------------------------
    def test_selected_author_invalid_request_method(self):
        response = self.anonymous_client.post(reverse('author', kwargs={'author_id': 10000}))

        self.assertEqual(response.resolver_match.func, selected_author)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_selected_author_not_exists(self):
        response = self.anonymous_client.get(reverse('author', kwargs={'author_id': 10000}))

        self.assertEqual(response.resolver_match.func, selected_author)
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------------------------------------------------------
    def test_selected_author(self):
        response = self.anonymous_client.get(reverse('author', kwargs={'author_id': self.author1.id}))

        self.assertEqual(response.resolver_match.func, selected_author)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'selected_author.html')
        self.assertIn('author', response.context)
        self.assertIn('books', response.context)
        self.assertEqual(response.context['author'].author_name, 'SomeAuthorCategoryName')
        self.assertEqual(response.context['author'].id, self.author1.id)
        self.assertEqual(len(response.context['books']), 1)
        self.assertEqual(response.context['books'][0].book_name, 'category_book_test1')