# -*- coding: utf-8 -*-

import os

from django.contrib import auth
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client

from ..models import TheUser, Category, Author, Language, Book, AddedBook
from .. import recommend

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(TEST_DIR, 'fixtures')


# ----------------------------------------------------------------------------------------------------------------------
class RecommendTest(TestCase):

    # @todo NOT FINISHED TESTS
    # @todo NOT FINISHED TESTS

    # ------------------------------------------------------------------------------------------------------------------
    def setUp(self):
        self.setup_users()
        self.setup_categories()
        self.setup_authors()
        self.setup_languages()
        self.setup_books()
        self.setup_added_books()

        recommend.START_RECOMMEND = 4

    # ------------------------------------------------------------------------------------------------------------------
    def setup_users(self):
        client = Client()
        self.anonymous_user = auth.get_user(client)

        self.user1 = User.objects.create_user('user1', 'user1@user1.com', 'testpassword1')
        self.user2 = User.objects.create_user('user2', 'user2@user2.com', 'testpassword2')

        self.the_user1 = TheUser.objects.get(id_user=self.user1)
        self.the_user2 = TheUser.objects.get(id_user=self.user2)

    # ------------------------------------------------------------------------------------------------------------------
    def setup_categories(self):
        self.category1 = Category.objects.create(category_name='category1')
        self.category2 = Category.objects.create(category_name='category2')

    # ------------------------------------------------------------------------------------------------------------------
    def setup_authors(self):
        self.author1 = Author.objects.create(author_name='Author 1')

    # ------------------------------------------------------------------------------------------------------------------
    def setup_languages(self):
        self.language = Language.objects.create(language='English')

    # ------------------------------------------------------------------------------------------------------------------
    def setup_books(self):
        self.book1 = self.create_book('Book 1', self.category1, self.the_user1)
        self.book2 = self.create_book('Book 2', self.category1, self.the_user1)
        self.book3 = self.create_book('Book 3', self.category1, self.the_user1)
        self.book4 = self.create_book('Book 4', self.category2, self.the_user1)
        self.book5 = self.create_book('Book 5', self.category2, self.the_user1)
        self.book6 = self.create_book('Book 6', self.category2, self.the_user1, True)
        self.book7 = self.create_book('Book 7', self.category1, self.the_user2, True)
        self.book8 = self.create_book('Book 8', self.category1, self.the_user2)
        self.book9 = self.create_book('Book 9', self.category1, self.the_user2)
        self.book10 = self.create_book('Book 10', self.category2, self.the_user2)
        self.book11 = self.create_book('Book 11', self.category2, self.the_user2)
        self.book12 = self.create_book('Book 12', self.category2, self.the_user2)
        self.book13 = self.create_book('Book 13', self.category2, self.the_user2)
        self.book14 = self.create_book('Book 14', self.category2, self.the_user2)

    # ------------------------------------------------------------------------------------------------------------------
    def create_book(self, name, category, who_added, private=False):
        test_book_path = os.path.join(TEST_DATA_DIR, 'test_book.pdf')

        return Book.objects.create(
            book_name=name,
            id_author=self.author1,
            id_category=category,
            language=self.language,
            book_file=SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
            who_added=who_added,
            private_book=private
        )

    # ------------------------------------------------------------------------------------------------------------------
    def setup_added_books(self):
        AddedBook.objects.create(id_user=self.the_user1, id_book=self.book1)
        AddedBook.objects.create(id_user=self.the_user1, id_book=self.book7)
        AddedBook.objects.create(id_user=self.the_user2, id_book=self.book2)
        AddedBook.objects.create(id_user=self.the_user2, id_book=self.book7)

    # ------------------------------------------------------------------------------------------------------------------
    def tearDown(self):
        for book in Book.objects.all():
            if os.path.exists(book.book_file.path):
                os.remove(book.book_file.path)
            if book.photo and os.path.exists(book.photo.path):
                os.remove(book.photo.path)

        recommend.START_RECOMMEND = 10
