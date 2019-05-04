# -*- coding: utf-8 -*-

import os

from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from ..admin import TheUserAdmin, BookAdmin, BookRatingAdmin
from ..models import TheUser, Book, Category, Language, Author, BookRating

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(TEST_DIR, 'fixtures')

TEST_BOOK_PATH = os.path.join(TEST_DATA_DIR, 'test_book.pdf')


# ----------------------------------------------------------------------------------------------------------------------
class AdminTest(TestCase):

    # ------------------------------------------------------------------------------------------------------------------
    def setUp(self):
        self.user1 = User.objects.create_user('new_user1', 'new_user1@mail.com', 'testpassword1')
        self.the_user1 = TheUser.objects.get(id_user=self.user1)

        self.category = Category.objects.create(category_name='Category')
        self.language = Language.objects.create(language='English')
        self.author = Author.objects.create(author_name='Author')

        self.book = Book.objects.create(
            book_name='Book',
            id_author=self.author,
            id_category=self.category,
            language=self.language,
            book_file=SimpleUploadedFile('test_book.pdf', open(TEST_BOOK_PATH, 'rb').read()),
            who_added=self.the_user1,
            extension=Book.EXT_CHOICES[0][0]
        )

        self.rating_obj = BookRating.objects.create(id_user=self.the_user1, id_book=self.book, rating=5)

        self.site = AdminSite()

    # ------------------------------------------------------------------------------------------------------------------
    def test_the_user(self):
        self.assertEqual(TheUserAdmin.username(self.the_user1), self.user1.username)
        self.assertEqual(TheUserAdmin.email(self.the_user1), self.user1.email)
        self.assertEqual(TheUserAdmin.date_joined(self.the_user1), self.user1.date_joined)

    # ------------------------------------------------------------------------------------------------------------------
    def test_book(self):
        self.assertEqual(BookAdmin.author(self.book), self.author.author_name)
        self.assertEqual(BookAdmin.category(self.book), self.category.category_name)
        self.assertEqual(BookAdmin.language(self.book), self.language.language)

    # ------------------------------------------------------------------------------------------------------------------
    def test_general_book(self):
        """
        Tests 'BookGeneral' admin class.

        Can be used any 'BookRatingAdmin', 'BookCommentAdmin' or 'AddedBookAdmin' child class, because here
        parent class is testing.
        """
        self.assertEqual(BookRatingAdmin.user(self.rating_obj), self.the_user1)
        self.assertEqual(BookRatingAdmin.book(self.rating_obj), '({}) {}'.format(self.book.id, self.book))

    # ------------------------------------------------------------------------------------------------------------------
    def tearDown(self):
        for book in Book.objects.all():
            if os.path.exists(book.book_file.path):
                os.remove(book.book_file.path)
            if book.photo and os.path.exists(book.photo.path):
                os.remove(book.photo.path)
