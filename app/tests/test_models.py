# -*- coding: utf-8 -*-

import copy
import os

from django.contrib import auth
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import QuerySet
from django.test import TestCase, Client, mock
from django.urls import reverse

from ..forms import AddBookForm
from ..models import (TheUser, Category, Author, Language, Book,
                      AddedBook, BookRating, BookComment, Post, SupportMessage, BookRelatedData)

from .utils import Utils

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(TEST_DIR, 'fixtures')


# ----------------------------------------------------------------------------------------------------------------------
class ModelTest(TestCase):

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def setUpTestData(cls):
        cls.setup_users()
        cls.setup_categories()
        cls.setup_authors()
        cls.setup_languages()
        cls.setup_books()
        cls.setup_added_books()
        cls.setup_book_rating()
        cls.setup_book_comment()
        cls.setup_post_messages()
        cls.setup_support_messages()

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def setup_users(cls):
        client = Client()
        cls.anonymous_user = auth.get_user(client)

        cls.user1 = User.objects.create_user('user1', 'user1@user1.com', 'testpassword1')
        cls.user2 = User.objects.create_user('user2', 'user2@user2.com', 'testpassword2')
        cls.user3 = User.objects.create_user('user3', 'user3@user3.com', 'testpassword3')
        cls.user4 = User.objects.create_user('user4', 'user4@user4.com', 'testpassword4')
        cls.user5 = User.objects.create_user('user5', 'user5@user5.com', 'testpassword5')
        cls.user6 = User.objects.create_user('user6', 'user6@user6.com', 'testpassword6')

        cls.the_user1 = TheUser.objects.get(id_user=cls.user1)
        cls.the_user2 = TheUser.objects.get(id_user=cls.user2)
        cls.the_user5 = TheUser.objects.get(id_user=cls.user5)
        cls.the_user6 = TheUser.objects.get(id_user=cls.user6)

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def setup_categories(cls):
        cls.category1 = Category.objects.create(category_name='category1')
        cls.category2 = Category.objects.create(category_name='category2')

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def setup_authors(cls):
        cls.author1 = Author.objects.create(author_name='Best Author 1')
        cls.author2 = Author.objects.create(author_name='trueAuthorNew')
        cls.author3 = Author.objects.create(author_name='zlast author')
        cls.author4 = Author.objects.create(author_name='<AuthorSpecialSymbols>&"')
        cls.author5 = Author.objects.create(author_name="O'Connor")

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def setup_languages(cls):
        cls.language_en = Language.objects.create(language='English')
        cls.language_ru = Language.objects.create(language='Russian')

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def setup_books(cls):
        test_book_path = os.path.join(TEST_DATA_DIR, 'test_book.pdf')
        test_book_image_path = os.path.join(TEST_DATA_DIR, 'test_book_image.png')

        books_setup = [
            {
                'name': 'First Book',
                'author': cls.author1,
                'category': cls.category1,
                'language': cls.language_en,
                'file': SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
                'photo': SimpleUploadedFile('test_book_image.png', open(test_book_image_path, 'rb').read()),
                'who_added': cls.the_user1,
                'private': True
            },
            {
                'name': 'Second Book',
                'author': cls.author2,
                'category': cls.category1,
                'language': cls.language_en,
                'file': SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
                'who_added': cls.the_user2,
                'blocked_book': True
            },
            {
                'name': 'Third Book',
                'author': cls.author2,
                'category': cls.category1,
                'language': cls.language_ru,
                'file': SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
                'photo': SimpleUploadedFile('test_book_image.png', open(test_book_image_path, 'rb').read()),
                'who_added': cls.the_user1,
                'blocked_book': True
            },
            {
                'name': 'Fourth Book',
                'author': cls.author1,
                'category': cls.category1,
                'language': cls.language_ru,
                'file': SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
                'photo': SimpleUploadedFile('test_book_image.png', open(test_book_image_path, 'rb').read()),
                'who_added': cls.the_user2,
                'blocked_book': True
            },
            {
                'name': 'Fifth Book',
                'author': cls.author1,
                'category': cls.category2,
                'language': cls.language_ru,
                'file': SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
                'who_added': cls.the_user1,
                'private': True
            },
            {
                'name': 'Sixth Book',
                'author': cls.author2,
                'category': cls.category2,
                'language': cls.language_en,
                'file': SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
                'photo': SimpleUploadedFile('test_book_image.png', open(test_book_image_path, 'rb').read()),
                'who_added': cls.the_user2
            },
            {
                'name': 'Seventh Book<>&"',
                'author': cls.author4,
                'category': cls.category2,
                'language': cls.language_en,
                'file': SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
                'photo': SimpleUploadedFile('test_book_image.png', open(test_book_image_path, 'rb').read()),
                'who_added': cls.the_user2
            }
        ]

        for book in books_setup:
            Book.objects.create(
                book_name=book['name'],
                id_author=book['author'],
                id_category=book['category'],
                description='TEST description',
                language=book['language'],
                book_file=book['file'],
                photo=book.get('photo', False),
                who_added=book['who_added'],
                private_book=book.get('private', False),
                blocked_book=book.get('blocked_book', False)
            )

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def setup_added_books(cls):
        AddedBook.objects.create(id_user=cls.the_user1, id_book=Book.objects.get(book_name='Third Book'))
        AddedBook.objects.create(id_user=cls.the_user1, id_book=Book.objects.get(book_name='Sixth Book'))
        AddedBook.objects.create(id_user=cls.the_user1, id_book=Book.objects.get(book_name='Fourth Book'))
        AddedBook.objects.create(id_user=cls.the_user2, id_book=Book.objects.get(book_name='Third Book'))
        AddedBook.objects.create(id_user=cls.the_user2, id_book=Book.objects.get(book_name='Sixth Book'))
        AddedBook.objects.create(id_user=cls.the_user2, id_book=Book.objects.get(book_name='Second Book'))
        AddedBook.objects.create(id_user=cls.the_user5, id_book=Book.objects.get(book_name='Sixth Book'))
        AddedBook.objects.create(id_user=cls.the_user6, id_book=Book.objects.get(book_name='Sixth Book'))

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def setup_book_rating(cls):
        BookRating.objects.create(id_book=Book.objects.get(book_name='Third Book'), id_user=cls.the_user1, rating=10)
        BookRating.objects.create(id_book=Book.objects.get(book_name='Third Book'), id_user=cls.the_user2, rating=5)
        BookRating.objects.create(id_book=Book.objects.get(book_name='Third Book'), id_user=cls.the_user5, rating=3)
        BookRating.objects.create(id_book=Book.objects.get(book_name='Fourth Book'), id_user=cls.the_user1, rating=7)
        BookRating.objects.create(id_book=Book.objects.get(book_name='Sixth Book'), id_user=cls.the_user1, rating=4)
        BookRating.objects.create(id_book=Book.objects.get(book_name='Second Book'), id_user=cls.the_user2, rating=7)

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def setup_book_comment(cls):
        second_book = Book.objects.get(book_name='Second Book')
        third_book = Book.objects.get(book_name='Third Book')
        fourth_book = Book.objects.get(book_name='Fourth Book')

        BookComment.objects.create(id_book=second_book, id_user=cls.the_user1, text='Test book 2 user 1')
        BookComment.objects.create(id_book=second_book, id_user=cls.the_user2, text='Test book 2 user 2')
        BookComment.objects.create(id_book=third_book, id_user=cls.the_user1, text='Test book 3 user 1')
        BookComment.objects.create(id_book=fourth_book, id_user=cls.the_user1, text='Test book 4 user 1')
        BookComment.objects.create(id_book=fourth_book, id_user=cls.the_user5, text='Test book 4 user 5')

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    @mock.patch('app.signals.email_dispatch.apply_async', new=mock.Mock())
    def setup_post_messages(cls):
        Post.objects.create(user=cls.the_user1, heading='post 1', text='Posted test text 1')
        Post.objects.create(user=cls.the_user1, heading='post 2', text='Posted test text 2')
        Post.objects.create(user=cls.the_user2, heading='post 3', text='Posted test text 3')

    # ------------------------------------------------------------------------------------------------------------------
    @classmethod
    def setup_support_messages(cls):
        SupportMessage.objects.create(email='testemail1@mail.co', text='Test text1')
        SupportMessage.objects.create(email='testemail1@mail.co', text='Test text2')
        SupportMessage.objects.create(email='test_email22@mail.co', text='Test text3')
        SupportMessage.objects.create(email='test_email23@mail.co', text='Test text4')

    # ------------------------------------------------------------------------------------------------------------------
    def test_the_user_str(self):
        self.assertEqual(str(self.the_user1), 'user1')
        self.assertEqual(str(self.the_user2), 'user2')

    # ------------------------------------------------------------------------------------------------------------------
    def test_creating_the_user_objects(self):
        """
        Must create 'app.models.TheUser' instance after django User instance was created.
        """
        self.assertEqual(User.objects.all().count(), 6)
        self.assertEqual(User.objects.all().count(), TheUser.objects.all().count())
        self.assertNotEqual(self.the_user1.auth_token, '')
        self.assertNotEqual(self.the_user1.auth_token, self.the_user2.auth_token)

    # ------------------------------------------------------------------------------------------------------------------
    def test_the_user_get_api_reminders(self):
        reminders = self.the_user1.get_api_reminders()
        reminders_keys_correct = ['vk', 'fb_group', 'fb_page', 'twitter', 'disabled_all', 'app_rate']

        self.assertTrue(isinstance(reminders, dict))
        self.assertEqual(sorted(list(reminders.keys())), sorted(reminders_keys_correct))

    # ------------------------------------------------------------------------------------------------------------------
    def test_the_user_get_web_reminders(self):
        reminders = self.the_user1.get_web_reminders()
        reminders_keys_correct = ['vk', 'fb_group', 'fb_page', 'twitter', 'disabled_all', 'app_download']

        self.assertTrue(isinstance(reminders, dict))
        self.assertEqual(sorted(list(reminders.keys())), sorted(reminders_keys_correct))

    # ------------------------------------------------------------------------------------------------------------------
    def test_the_user_update_reminder(self):
        reminders = self.the_user1.get_web_reminders()

        self.assertTrue(isinstance(reminders, dict))
        self.assertEqual(reminders['vk'], True)
        self.assertEqual(reminders['app_download'], True)

        self.the_user1.update_reminder('vk', False)
        self.the_user1.update_reminder('app_download', False)

        updated_reminders = self.the_user1.get_web_reminders()
        self.assertTrue(isinstance(updated_reminders, dict))
        self.assertEqual(updated_reminders['vk'], False)
        self.assertEqual(updated_reminders['app_download'], False)

    # ------------------------------------------------------------------------------------------------------------------
    def test_removing_user_objects(self):
        """
        Must remove django User instance after 'app.models.TheUser' objects was deleted.
        """
        the_user3 = TheUser.objects.get(id_user__username='user3')
        the_user4 = TheUser.objects.get(id_user__email='user4@user4.com')

        the_user3.delete()
        the_user4.delete()

        self.assertEqual(User.objects.all().count(), 4)
        self.assertEqual(User.objects.all().count(), TheUser.objects.all().count())

    # ------------------------------------------------------------------------------------------------------------------
    def test_created_categories(self):
        self.assertEqual(Category.objects.all().count(), 2)
        self.assertNotEqual(self.category1, self.category2)

    # ------------------------------------------------------------------------------------------------------------------
    def test_categories_str(self):
        self.assertEqual(str(self.category1), 'category1')
        self.assertEqual(str(self.category2), 'category2')

    # ------------------------------------------------------------------------------------------------------------------
    def test_created_authors(self):
        self.assertEqual(Author.objects.all().count(), 5)
        self.assertNotEqual(self.author1, self.author2)

    # ------------------------------------------------------------------------------------------------------------------
    def test_get_authors_list(self):
        """
        Must return authors list depending on different letters/letter case/words/symbols.
        """
        self.assertEqual(Author.get_authors_list('bEst'), ['Best Author 1'])
        self.assertEqual(Author.get_authors_list('1'), ['Best Author 1'])
        self.assertEqual(Author.get_authors_list(' '), ['Best Author 1', 'zlast author'])
        self.assertEqual(Author.get_authors_list('new'), ['trueAuthorNew'])
        self.assertEqual(Author.get_authors_list('TRUE'), ['trueAuthorNew'])
        self.assertEqual(Author.get_authors_list('Best Author 1'), ['Best Author 1'])
        self.assertEqual(Author.get_authors_list('trueAuthorNew'), ['trueAuthorNew'])

    # ------------------------------------------------------------------------------------------------------------------
    def test_get_authors_list_with_escaping(self):
        self.assertEqual(Author.get_authors_list("'", True), ['O&#39;Connor'])
        self.assertEqual(Author.get_authors_list("Connor", True), ['O&#39;Connor'])
        self.assertEqual(
            Author.get_authors_list('b', True),
            ['Best Author 1', '&lt;AuthorSpecialSymbols&gt;&amp;&quot;']
        )
        self.assertEqual(
            Author.get_authors_list('e', True),
            ['Best Author 1', 'trueAuthorNew', '&lt;AuthorSpecialSymbols&gt;&amp;&quot;']
        )
        self.assertEqual(
            Author.get_authors_list('author', True),
            ['Best Author 1', 'trueAuthorNew', 'zlast author', '&lt;AuthorSpecialSymbols&gt;&amp;&quot;']
        )

    # ------------------------------------------------------------------------------------------------------------------
    def test_get_authors_list_without_escaping(self):
        self.assertEqual(Author.get_authors_list("'"), ["O'Connor"])
        self.assertEqual(Author.get_authors_list("Connor", False), ["O'Connor"])
        self.assertEqual(Author.get_authors_list('b'), ['Best Author 1', '<AuthorSpecialSymbols>&"'])
        self.assertEqual(
            Author.get_authors_list('e'),
            ['Best Author 1', 'trueAuthorNew', '<AuthorSpecialSymbols>&"']
        )
        self.assertEqual(
            Author.get_authors_list('author', False),
            ['Best Author 1', 'trueAuthorNew', 'zlast author', '<AuthorSpecialSymbols>&"']
        )

    # ------------------------------------------------------------------------------------------------------------------
    def test_created_language(self):
        self.assertEqual(Language.objects.all().count(), 2)
        self.assertNotEqual(self.author1, self.author2)

    # ------------------------------------------------------------------------------------------------------------------
    def test_created_books(self):
        books = Book.objects.all()

        self.assertEqual(books.count(), 7)
        self.assertEqual(books.filter(private_book=True).count(), 2)
        self.assertEqual(books.filter(id_category=self.category1).count(), 4)
        self.assertEqual(books.filter(id_author=self.author1).count(), 3)
        self.assertEqual(books.filter(language=self.language_en).count(), 4)
        self.assertEqual(books.filter(photo=False).count(), 2)
        self.assertEqual(books.filter(who_added=self.the_user1).count(), 3)
        self.assertEqual(books.filter(id_category=self.category2, id_author=self.author2).count(), 1)
        self.assertEqual(books.filter(id_category=self.category1,
                                      id_author=self.author2,
                                      language=self.language_ru,
                                      who_added=self.the_user1).count(), 1)
        self.assertEqual(books.filter(id_category=self.category1,
                                      id_author=self.author2,
                                      language=self.language_ru,
                                      who_added=self.the_user2).count(), 0)
        self.assertEqual(books.filter(blocked_book=True).count(), 3)

    # ------------------------------------------------------------------------------------------------------------------
    def test_get_related_objects_for_create(self):
        test_book_path = os.path.join(TEST_DATA_DIR, 'test_book.pdf')

        form_data = {
            'bookname': 'The new book',
            'author': 'trueAuthorNew',
            'category': 'category1',
            'language': 'English',
            'about': 'about book',
            'bookfile': SimpleUploadedFile('test_book.pdf', open(test_book_path, 'rb').read()),
        }

        form_data_new_author = copy.deepcopy(form_data)
        form_data_new_author['author'] = 'super new author'

        self.assertEqual(Author.objects.all().count(), 5)

        form = AddBookForm(data=form_data)
        form.is_valid()
        form_with_new_author = AddBookForm(data=form_data_new_author)
        form_with_new_author.is_valid()

        related_data = Book.get_related_objects_for_create(self.user1.id, form)

        self.assertTrue(isinstance(related_data, BookRelatedData))
        self.assertEqual(len(related_data), 4)
        self.assertEqual(related_data.author, Author.objects.get(author_name='trueAuthorNew'))
        self.assertEqual(Author.objects.all().count(), 5)

        related_data_new_author = Book.get_related_objects_for_create(self.user1.id, form_with_new_author)

        self.assertTrue(isinstance(related_data, BookRelatedData))
        self.assertEqual(len(related_data_new_author), 4)
        self.assertEqual(related_data_new_author.author, Author.objects.get(author_name='super new author'))
        self.assertEqual(Author.objects.all().count(), 6)

    # ------------------------------------------------------------------------------------------------------------------
    def test_get_related_objects_create_api(self):
        """
        Must generate Book related data when creates a Book object for API calls.
        New author must be returned if it's name not present in the Author model.
        """
        test_data = {'author': 'trueAuthorNew', 'category': 'category2', 'language': 'Russian'}
        test_data_new_author = {'author': 'NEW AUTHOR', 'category': 'category1', 'language': 'English'}

        self.assertEqual(
            Book.get_related_objects_create_api(self.the_user1, test_data),
            BookRelatedData(self.author2, self.category2, self.language_ru, None)
        )
        self.assertEqual(Author.objects.all().count(), 5)

        self.assertEqual(
            Book.get_related_objects_create_api(self.the_user1, test_data_new_author),
            BookRelatedData(Author.objects.get(author_name='NEW AUTHOR'), self.category1, self.language_en, None)
        )
        self.assertEqual(Author.objects.all().count(), 6)

    # ------------------------------------------------------------------------------------------------------------------
    def test_get_related_objects_selected_book_unknown_user(self):
        """
        Must generate selected book related data for unknown (anonymous) users.
        """
        third_book = Book.objects.get(book_name='Third Book')
        sixth_book = Book.objects.get(book_name='Sixth Book')

        self.assertTrue(isinstance(Book.get_related_objects_selected_book(self.anonymous_user, third_book.id), dict))

        related_third_book = Book.get_related_objects_selected_book(self.anonymous_user, third_book.id)
        related_sixth_book = Book.get_related_objects_selected_book(self.anonymous_user, sixth_book.id)

        self.assertEqual(related_third_book['book'], third_book)
        self.assertEqual(related_third_book['avg_book_rating'], {'rating__avg': 6.0})
        self.assertEqual(related_third_book['book_rating_count'], 3)
        self.assertEqual(related_third_book['added_book'], None)
        self.assertEqual(related_third_book['comments'].count(), 1)
        self.assertEqual(related_third_book['comments'][0],
                         BookComment.objects.filter(id_book=third_book).order_by('-id')[0])

        self.assertEqual(related_sixth_book['book'], sixth_book)
        self.assertEqual(related_sixth_book['avg_book_rating'], {'rating__avg': 4.0})
        self.assertEqual(related_sixth_book['book_rating_count'], 1)
        self.assertEqual(related_sixth_book['added_book'], None)
        self.assertEqual(related_sixth_book['comments'].count(), 0)

        AddedBook.objects.create(id_user=self.the_user5, id_book=third_book)
        BookRating.objects.create(id_user=self.the_user6, id_book=third_book, rating=10)
        BookComment.objects.create(id_user=self.the_user6, id_book=third_book, text='TEST TEXT 2')

        related_third_book = Book.get_related_objects_selected_book(self.anonymous_user, third_book.id)

        self.assertEqual(related_third_book['book'], third_book)
        self.assertEqual(related_third_book['avg_book_rating'], {'rating__avg': 7.0})
        self.assertEqual(related_third_book['book_rating_count'], 4)
        self.assertEqual(related_third_book['added_book'], None)
        self.assertEqual(related_third_book['comments'].count(), 2)

    # ------------------------------------------------------------------------------------------------------------------
    def test_get_related_objects_selected_book_added_user(self):
        """
        This case is testing only 'added_book' param, because for
        user who is reading the book only this attribute will change relatively to function above.
        """
        third_book = Book.objects.get(book_name='Third Book')
        sixth_book = Book.objects.get(book_name='Sixth Book')

        self.assertTrue(isinstance(Book.get_related_objects_selected_book(self.the_user1.id_user, third_book.id), dict))

        related_third_book = Book.get_related_objects_selected_book(self.the_user1.id_user, third_book.id)
        related_sixth_book = Book.get_related_objects_selected_book(self.the_user1.id_user, sixth_book.id)

        self.assertEqual(related_third_book['added_book'],
                         AddedBook.objects.get(id_book=third_book, id_user=self.the_user1))
        self.assertEqual(related_sixth_book['added_book'],
                         AddedBook.objects.get(id_book=sixth_book, id_user=self.the_user1))

    # ------------------------------------------------------------------------------------------------------------------
    def test_get_related_objects_selected_book_with_user_key(self):
        """
        Tests returning data for related objects for selected book with 'user_key' attribute, meaning that
        user is anonymous (i.e. not logged) but with using user key. Done for API requests access.
        """
        third_book = Book.objects.get(book_name='Third Book')
        related_third_book = Book.get_related_objects_selected_book(
            self.anonymous_user, third_book.id, self.the_user1.auth_token
        )

        self.assertEqual(related_third_book['book'], third_book)
        self.assertEqual(related_third_book['avg_book_rating'], {'rating__avg': 6.0})
        self.assertEqual(related_third_book['book_rating_count'], 3)
        self.assertEqual(related_third_book['added_book'],
                         AddedBook.objects.get(id_book=third_book, id_user=self.the_user1))
        self.assertEqual(related_third_book['comments'].count(), 1)
        self.assertEqual(related_third_book['comments'][0],
                         BookComment.objects.filter(id_book=third_book).order_by('-id')[0])

    # ------------------------------------------------------------------------------------------------------------------
    def test_sort_by_book_name_category1(self):
        """
        Must generate correct dictionaries for anonymous users, users with private books and without.
        Testing first category.
        """
        first_book = Book.objects.get(book_name='First Book')
        third_book = Book.objects.get(book_name='Third Book')
        fourth_book = Book.objects.get(book_name='Fourth Book')
        first_book_dict = Utils.generate_sort_dict(first_book)
        third_book_dict = Utils.generate_sort_dict(third_book)
        fourth_book_dict = Utils.generate_sort_dict(fourth_book)

        self.assertTrue(isinstance(Book.sort_by_book_name(self.anonymous_user, self.category1), list))
        self.assertEqual(len(Book.sort_by_book_name(self.anonymous_user, self.category1)), 3)
        self.assertEqual(Book.sort_by_book_name(self.anonymous_user, self.category1)[0], fourth_book_dict)
        self.assertEqual(Book.sort_by_book_name(self.anonymous_user, self.category1)[2], third_book_dict)

        self.assertEqual(len(Book.sort_by_book_name(self.the_user2.id_user, self.category1)), 3)
        self.assertEqual(Book.sort_by_book_name(self.the_user2.id_user, self.category1)[0], fourth_book_dict)
        self.assertEqual(Book.sort_by_book_name(self.the_user2.id_user, self.category1)[2], third_book_dict)

        self.assertEqual(len(Book.sort_by_book_name(self.the_user1.id_user, self.category1)), 4)
        self.assertEqual(Book.sort_by_book_name(self.the_user1.id_user, self.category1)[0], first_book_dict)
        self.assertEqual(Book.sort_by_book_name(self.the_user1.id_user, self.category1)[3], third_book_dict)

    # ------------------------------------------------------------------------------------------------------------------
    def test_sort_by_book_name_category2(self):
        """
        Must generate correct dictionaries for anonymous users, users with private books and without.
        Testing first category.
        """
        fifth_book = Book.objects.get(book_name='Fifth Book')
        seventh_book = Book.objects.get(book_name='Seventh Book<>&"')

        fifth_book_dict = Utils.generate_sort_dict(fifth_book)
        seventh_book_dict = Utils.generate_sort_dict(seventh_book)

        self.assertEqual(len(Book.sort_by_book_name(self.anonymous_user, self.category2)), 2)
        self.assertEqual(Book.sort_by_book_name(self.anonymous_user, self.category2)[0], seventh_book_dict)

        self.assertEqual(len(Book.sort_by_book_name(self.the_user2.id_user, self.category2)), 2)
        self.assertEqual(Book.sort_by_book_name(self.the_user2.id_user, self.category2)[0], seventh_book_dict)

        self.assertEqual(len(Book.sort_by_book_name(self.the_user1.id_user, self.category2)), 3)
        self.assertEqual(Book.sort_by_book_name(self.the_user1.id_user, self.category2)[0], fifth_book_dict)
        self.assertEqual(Book.sort_by_book_name(self.the_user1.id_user, self.category2)[1], seventh_book_dict)

    # ------------------------------------------------------------------------------------------------------------------
    def test_sort_by_author_category1(self):
        """
        Must generate correct dictionaries for anonymous users, users with private books and without.
        Testing returned book authors at first category.
        """
        self.assertTrue(isinstance(Book.sort_by_author(self.anonymous_user, self.category1), list))
        self.assertEqual(len(Book.sort_by_author(self.anonymous_user, self.category1)), 3)
        self.assertEqual(Book.sort_by_author(self.anonymous_user, self.category1)[0]['author'],
                         self.author1.author_name)
        self.assertEqual(Book.sort_by_author(self.anonymous_user, self.category1)[2]['author'],
                         self.author2.author_name)

        self.assertEqual(len(Book.sort_by_author(self.the_user2.id_user, self.category1)), 3)
        self.assertEqual(Book.sort_by_author(self.the_user2.id_user, self.category1)[0]['author'],
                         self.author1.author_name)
        self.assertEqual(Book.sort_by_author(self.the_user2.id_user, self.category1)[2]['author'],
                         self.author2.author_name)

        self.assertEqual(len(Book.sort_by_author(self.the_user1.id_user, self.category1)), 4)
        self.assertEqual(Book.sort_by_author(self.the_user1.id_user, self.category1)[0]['author'],
                         self.author1.author_name)
        self.assertEqual(Book.sort_by_author(self.the_user1.id_user, self.category1)[3]['author'],
                         self.author2.author_name)

    # ------------------------------------------------------------------------------------------------------------------
    def test_sort_by_author_category2(self):
        """
        Must generate correct dictionaries for anonymous users, users with private books and without.
        Testing returned book authors at second category.
        """
        escaped_author_name = '&lt;AuthorSpecialSymbols&gt;&amp;&quot;'

        self.assertEqual(len(Book.sort_by_author(self.anonymous_user, self.category2)), 2)
        self.assertEqual(Book.sort_by_author(self.anonymous_user, self.category2)[0]['author'], escaped_author_name)

        self.assertEqual(len(Book.sort_by_author(self.the_user2.id_user, self.category2)), 2)
        self.assertEqual(Book.sort_by_author(self.the_user2.id_user, self.category2)[0]['author'], escaped_author_name)

        self.assertEqual(len(Book.sort_by_author(self.the_user1.id_user, self.category2)), 3)
        self.assertEqual(Book.sort_by_author(self.the_user1.id_user, self.category2)[0]['author'], escaped_author_name)
        self.assertEqual(Book.sort_by_author(self.the_user1.id_user, self.category2)[1]['author'],
                         self.author1.author_name)

    # ------------------------------------------------------------------------------------------------------------------
    def test_sort_by_estimation_category1(self):
        """
        Must generate correct dictionaries for anonymous users, users with private books and without.
        Testing returned book rating at first category.
        """
        self.assertTrue(isinstance(Book.sort_by_estimation(self.anonymous_user, self.category1), list))
        self.assertEqual(len(Book.sort_by_estimation(self.anonymous_user, self.category1)), 3)
        self.assertEqual(Book.sort_by_estimation(self.anonymous_user, self.category1)[0]['rating'], 7)
        self.assertEqual(Book.sort_by_estimation(self.anonymous_user, self.category1)[2]['rating'], 6)

        self.assertEqual(len(Book.sort_by_estimation(self.the_user2.id_user, self.category1)), 3)
        self.assertEqual(Book.sort_by_estimation(self.the_user2.id_user, self.category1)[0]['rating'], 7)
        self.assertEqual(Book.sort_by_estimation(self.the_user2.id_user, self.category1)[2]['rating'], 6)

        self.assertEqual(len(Book.sort_by_estimation(self.the_user1.id_user, self.category1)), 4)
        self.assertEqual(Book.sort_by_estimation(self.the_user1.id_user, self.category1)[0]['rating'], 7)
        self.assertEqual(Book.sort_by_estimation(self.the_user1.id_user, self.category1)[2]['rating'], 6)

    # ------------------------------------------------------------------------------------------------------------------
    def test_sort_by_estimation_category2(self):
        """
        Must generate correct dictionaries for anonymous users, users with private books and without.
        Testing returned book rating at second category.
        """
        self.assertEqual(len(Book.sort_by_estimation(self.anonymous_user, self.category2)), 2)
        self.assertEqual(Book.sort_by_estimation(self.anonymous_user, self.category2)[0]['rating'], 4)

        self.assertEqual(len(Book.sort_by_estimation(self.the_user2.id_user, self.category2)), 2)
        self.assertEqual(Book.sort_by_estimation(self.the_user2.id_user, self.category2)[0]['rating'], 4)

        self.assertEqual(len(Book.sort_by_estimation(self.the_user1.id_user, self.category2)), 3)
        self.assertEqual(Book.sort_by_estimation(self.the_user1.id_user, self.category2)[0]['rating'], 4)
        self.assertEqual(Book.sort_by_estimation(self.the_user1.id_user, self.category2)[1]['rating'], None)

    # ------------------------------------------------------------------------------------------------------------------
    def test_sort_by_readable(self):
        """
        Must generate correct data by most readable books for anonymous users and users with private books.
        Testing count of sorted books with and without selected categories.
        """
        sorted_structure = Book.sort_by_readable(self.anonymous_user, self.category1)
        self.assertTrue(isinstance(sorted_structure, list))
        self.assertTrue(isinstance(sorted_structure[0], dict))
        self.assertEqual(set(sorted_structure[0].keys()), {'id', 'name', 'author', 'url'})

        self.assertEqual(len(Book.sort_by_readable(user=self.anonymous_user, category=self.category1)), 3)
        self.assertEqual(len(Book.sort_by_readable(user=self.anonymous_user, category=self.category1, count=2)), 2)
        self.assertEqual(len(Book.sort_by_readable(user=self.the_user1.id_user, category=self.category1)), 3)
        self.assertEqual(len(Book.sort_by_readable(user=self.the_user1.id_user, category=self.category1, count=2)), 2)
        self.assertEqual(len(Book.sort_by_readable(user=self.the_user2.id_user, category=self.category1)), 3)
        self.assertEqual(len(Book.sort_by_readable(user=self.the_user2.id_user, category=self.category1, count=2)), 2)

        self.assertEqual(len(Book.sort_by_readable(user=self.anonymous_user)), 4)
        self.assertEqual(len(Book.sort_by_readable(user=self.anonymous_user, count=2)), 2)
        self.assertEqual(len(Book.sort_by_readable(user=self.the_user1.id_user)), 4)
        self.assertEqual(len(Book.sort_by_readable(user=self.the_user1.id_user, count=3)), 3)
        self.assertEqual(len(Book.sort_by_readable(user=self.the_user2.id_user)), 4)
        self.assertEqual(len(Book.sort_by_readable(user=self.the_user2.id_user, count=2)), 2)

    # ------------------------------------------------------------------------------------------------------------------
    def test_generate_books(self):
        """
        Must generate correct dictionaries for Book data.
        """
        books = Book.objects.all()

        self.assertTrue(isinstance(Book.generate_books(books), list))
        self.assertEqual(len(Book.generate_books(books)), 7)
        self.assertEqual(len(Book.generate_books(books)[0].keys()), 5)
        self.assertEqual(Book.generate_books(books)[0], Utils.generate_sort_dict(books[0]))
        self.assertEqual(Book.generate_books(books)[6], Utils.generate_sort_dict(books[6]))

    # ------------------------------------------------------------------------------------------------------------------
    def test_fetch_books(self):
        """
        Must generate list of dicts with Books data depending on different criteria.
        """
        self.assertTrue(isinstance(Book.fetch_books('book'), list))

        self.assertEqual(len(Book.fetch_books('Second Book')), 1)
        self.assertEqual(len(Book.fetch_books('book')), 7)
        self.assertEqual(len(Book.fetch_books('ook')), 7)
        self.assertEqual(len(Book.fetch_books('trueAuthorNew')), 3)
        self.assertEqual(len(Book.fetch_books('author')), 7)
        self.assertEqual(len(Book.fetch_books('new')), 3)
        self.assertEqual(len(Book.fetch_books('True')), 3)

    # ------------------------------------------------------------------------------------------------------------------
    def test_generate_existing_books(self):
        """
        Must generate list of dicts with Books data depending on different criteria and excluding private books.
        """
        self.assertTrue(isinstance(Book.generate_existing_books('book'), list))
        self.assertEqual(len(Book.generate_existing_books('book')), 5)
        self.assertEqual(len(Book.generate_existing_books('Book')), 5)
        self.assertEqual(len(Book.generate_existing_books('bOoK')), 5)

        fourth_book = Book.objects.get(book_name='Fourth Book')
        test_book = Book.generate_existing_books('fourth')

        self.assertEqual(len(test_book), 1)
        self.assertTrue(isinstance(test_book[0], dict))
        self.assertEqual(test_book[0], {'url': reverse('book', args=[fourth_book.id]),
                                        'name': fourth_book.book_name})

        test_private_book = Book.generate_existing_books('fifth')

        self.assertEqual(len(test_private_book), 0)

    # ------------------------------------------------------------------------------------------------------------------
    def test_exclude_private_books(self):
        """
        Must generate query sets or lists with Books depending on user type.
        """
        all_books = Book.objects.all()
        list_all_books = list(all_books)

        self.assertEqual(Book.exclude_private_books(self.the_user1.id_user, all_books).count(), 7)
        self.assertEqual(Book.exclude_private_books(self.the_user2.id_user, all_books).count(), 5)
        self.assertTrue(isinstance(Book.exclude_private_books(self.the_user1.id_user, all_books), QuerySet))
        self.assertTrue(isinstance(Book.exclude_private_books(self.the_user2.id_user, all_books), QuerySet))

        self.assertEqual(len(Book.exclude_private_books(self.the_user1.id_user, list_all_books)), 7)
        self.assertEqual(len(Book.exclude_private_books(self.the_user2.id_user, list_all_books)), 5)
        self.assertTrue(isinstance(Book.exclude_private_books(self.the_user1.id_user, list_all_books), list))
        self.assertTrue(isinstance(Book.exclude_private_books(self.the_user2.id_user, list_all_books), list))

        self.assertTrue(self.anonymous_user.is_anonymous)
        self.assertEqual(Book.exclude_private_books(self.anonymous_user, all_books).count(), 5)
        self.assertEqual(len(Book.exclude_private_books(self.anonymous_user, list_all_books)), 5)
        self.assertTrue(isinstance(Book.exclude_private_books(self.anonymous_user, all_books), QuerySet))
        self.assertTrue(isinstance(Book.exclude_private_books(self.anonymous_user, list_all_books), list))

    # ------------------------------------------------------------------------------------------------------------------
    def test_added_books(self):
        self.assertEqual(AddedBook.objects.all().count(), 8)

        self.assertEqual(AddedBook.objects.filter(id_user=self.the_user1).count(), 3)
        self.assertEqual(AddedBook.objects.filter(id_user=self.the_user2).count(), 3)
        self.assertEqual(AddedBook.objects.filter(id_user=self.the_user5).count(), 1)
        self.assertEqual(AddedBook.objects.filter(id_user=self.the_user6).count(), 1)

        self.assertEqual(AddedBook.objects.filter(id_book=Book.objects.get(book_name='Sixth Book')).count(), 4)
        self.assertEqual(AddedBook.objects.filter(id_book=Book.objects.get(book_name='Third Book')).count(), 2)
        self.assertEqual(AddedBook.objects.filter(id_book=Book.objects.get(book_name='Fifth Book')).count(), 0)

        self.assertEqual(AddedBook.objects.filter(id_user=self.the_user1,
                                                  id_book=Book.objects.get(book_name='Third Book')).count(), 1)
        self.assertEqual(AddedBook.objects.filter(id_user=self.the_user1,
                                                  id_book=Book.objects.get(book_name='Sixth Book')).count(), 1)
        self.assertEqual(AddedBook.objects.filter(id_user=self.the_user2,
                                                  id_book=Book.objects.get(book_name='Sixth Book')).count(), 1)
        self.assertEqual(AddedBook.objects.filter(id_user=self.the_user2,
                                                  id_book=Book.objects.get(book_name='Fourth Book')).count(), 0)

    # ------------------------------------------------------------------------------------------------------------------
    def test_added_books_change(self):
        """
        Must save book page after changing it.
        """
        added_book3 = AddedBook.objects.get(id_user=self.the_user1, id_book=Book.objects.get(book_name='Third Book'))
        added_book6 = AddedBook.objects.get(id_user=self.the_user2, id_book=Book.objects.get(book_name='Sixth Book'))
        self.assertEqual(added_book3.last_page, 1)
        self.assertEqual(added_book6.last_page, 1)

        added_book3.last_page = 500
        added_book3.save()
        self.assertEqual(added_book3.last_page, 500)
        self.assertEqual(added_book6.last_page, 1)

        added_book6.last_page = 256
        added_book6.save()
        self.assertEqual(added_book3.last_page, 500)
        self.assertEqual(added_book6.last_page, 256)

    # ------------------------------------------------------------------------------------------------------------------
    def test_added_books_delete(self):
        added_book_third = AddedBook.objects.get(id_user=self.the_user1,
                                                 id_book=Book.objects.get(book_name='Third Book'))
        added_book_sixth = AddedBook.objects.get(id_user=self.the_user2,
                                                 id_book=Book.objects.get(book_name='Sixth Book'))
        added_book_third.delete()
        added_book_sixth.delete()

        self.assertEqual(AddedBook.objects.all().count(), 6)
        self.assertEqual(AddedBook.objects.filter(id_user=self.the_user1).count(), 2)
        self.assertEqual(AddedBook.objects.filter(id_user=self.the_user1).count(), 2)
        self.assertEqual(AddedBook.objects.filter(id_book=Book.objects.get(book_name='Sixth Book')).count(), 3)
        self.assertEqual(AddedBook.objects.filter(id_book=Book.objects.get(book_name='Third Book')).count(), 1)

        self.assertEqual(AddedBook.objects.filter(id_user=self.the_user1,
                                                  id_book=Book.objects.get(book_name='Third Book')).count(), 0)
        self.assertEqual(AddedBook.objects.filter(id_user=self.the_user2,
                                                  id_book=Book.objects.get(book_name='Sixth Book')).count(), 0)

    # ------------------------------------------------------------------------------------------------------------------
    def test_get_user_added_book(self):
        """
        Must generate list of books that added by user (reading by user).
        """
        self.assertTrue(self.anonymous_user.is_anonymous)
        self.assertEqual(len(AddedBook.get_user_added_books(self.anonymous_user)), 0)
        self.assertEqual(AddedBook.get_user_added_books(self.anonymous_user), [])

        self.assertEqual(AddedBook.get_user_added_books(self.the_user1.id_user).count(), 3)
        self.assertEqual(AddedBook.get_user_added_books(self.the_user5.id_user).count(), 1)
        self.assertNotEqual(AddedBook.get_user_added_books(self.the_user1.id_user), [])

        removed_obj = AddedBook.objects.get(id_book=Book.objects.get(book_name='Sixth Book'),
                                            id_user=self.the_user5)
        removed_obj.delete()

        self.assertEqual(AddedBook.get_user_added_books(self.the_user5.id_user).count(), 0)
        self.assertNotEqual(AddedBook.get_user_added_books(self.the_user5.id_user), [])

    # ------------------------------------------------------------------------------------------------------------------
    def test_get_count_added(self):
        """
        Must return count how many users is reading some book.
        """
        third_book = Book.objects.get(book_name='Third Book')
        sixth_book = Book.objects.get(book_name='Sixth Book')
        not_existing_id = 10000

        self.assertEqual(AddedBook.get_count_added(third_book.id), 2)
        self.assertEqual(AddedBook.get_count_added(sixth_book.id), 4)
        self.assertEqual(AddedBook.get_count_added(not_existing_id), 0)

        removed_third = AddedBook.objects.filter(id_user=self.the_user1, id_book=third_book)
        removed_third.delete()

        removed_sixth = AddedBook.objects.filter(id_user=self.the_user1, id_book=sixth_book)
        removed_sixth.delete()

        self.assertEqual(AddedBook.get_count_added(third_book.id), 1)
        self.assertEqual(AddedBook.get_count_added(sixth_book.id), 3)
        self.assertEqual(AddedBook.get_count_added(not_existing_id), 0)

    # ------------------------------------------------------------------------------------------------------------------
    def test_book_rating(self):
        self.assertEqual(BookRating.objects.all().count(), 6)
        self.assertEqual(BookRating.objects.filter(id_book=Book.objects.filter(book_name='Third Book')).count(), 3)
        self.assertEqual(BookRating.objects.filter(id_user=self.the_user1).count(), 3)
        self.assertEqual(BookRating.objects.filter(id_user=self.the_user2).count(), 2)
        self.assertEqual(BookRating.objects.filter(rating=7).count(), 2)

        self.assertEqual(BookRating.objects.filter(id_book=Book.objects.get(book_name='Third Book'),
                                                   id_user=self.the_user1).count(), 1)
        self.assertEqual(BookRating.objects.filter(id_book=Book.objects.get(book_name='Third Book'),
                                                   id_user=self.the_user6).count(), 0)
        self.assertEqual(BookRating.objects.filter(id_book=Book.objects.get(book_name='Fourth Book'),
                                                   id_user=self.the_user1,
                                                   rating=7).count(), 1)

    # ------------------------------------------------------------------------------------------------------------------
    def test_changed_book_rating(self):
        removed_rating = BookRating.objects.get(id_book=Book.objects.get(book_name='Third Book'),
                                                id_user=self.the_user1)
        removed_rating.delete()
        self.assertEqual(BookRating.objects.all().count(), 5)

        changed_rating1 = BookRating.objects.get(id_book=Book.objects.get(book_name='Second Book'),
                                                 id_user=self.the_user2)
        changed_rating2 = BookRating.objects.get(id_book=Book.objects.get(book_name='Fourth Book'),
                                                 id_user=self.the_user1)

        self.assertEqual(BookRating.objects.filter(rating=7).count(), 2)
        self.assertEqual(changed_rating1.rating, 7)
        self.assertEqual(changed_rating2.rating, 7)

        changed_rating1.rating = 4
        changed_rating1.save()

        changed_rating2.rating = 3
        changed_rating2.save()

        self.assertEqual(changed_rating1.rating, 4)
        self.assertEqual(changed_rating2.rating, 3)
        self.assertEqual(BookRating.objects.filter(rating=7).count(), 0)
        self.assertEqual(BookRating.objects.filter(rating=4).count(), 2)
        self.assertEqual(BookRating.objects.filter(rating=3).count(), 2)

    # ------------------------------------------------------------------------------------------------------------------
    def test_book_comment(self):
        self.assertEqual(BookComment.objects.all().count(), 5)
        self.assertEqual(BookComment.objects.filter(id_user=self.the_user1).count(), 3)
        self.assertEqual(BookComment.objects.filter(id_book=Book.objects.get(book_name='Second Book')).count(), 2)
        self.assertEqual(BookComment.objects.filter(id_book=Book.objects.get(book_name='Fourth Book')).count(), 2)
        self.assertEqual(BookComment.objects.filter(id_book=Book.objects.get(book_name='Sixth Book')).count(), 0)
        self.assertEqual(BookComment.objects.filter(id_user=self.the_user6).count(), 0)
        self.assertEqual(BookComment.objects.filter(id_book=Book.objects.get(book_name='Second Book'),
                                                    id_user=self.the_user1).count(), 1)

        BookComment.objects.create(id_book=Book.objects.get(book_name='Second Book'),
                                   id_user=self.the_user1,
                                   text='New comment user1 book 2')

        self.assertEqual(BookComment.objects.all().count(), 6)
        self.assertEqual(BookComment.objects.filter(id_user=self.the_user1).count(), 4)
        self.assertEqual(BookComment.objects.filter(id_book=Book.objects.get(book_name='Second Book')).count(), 3)
        self.assertEqual(BookComment.objects.filter(id_book=Book.objects.get(book_name='Second Book'),
                                                    id_user=self.the_user1).count(), 2)

        deleted_comment = BookComment.objects.get(id_book=Book.objects.get(book_name='Fourth Book'),
                                                  id_user=self.the_user5)
        deleted_comment.delete()

        self.assertEqual(BookComment.objects.all().count(), 5)
        self.assertEqual(BookComment.objects.filter(id_user=self.the_user5).count(), 0)
        self.assertEqual(BookComment.objects.filter(id_book=Book.objects.get(book_name='Fourth Book')).count(), 1)

    # ------------------------------------------------------------------------------------------------------------------
    def test_post_messages(self):
        self.assertEqual(Post.objects.all().count(), 3)
        self.assertEqual(Post.objects.filter(user=self.the_user1).count(), 2)
        self.assertEqual(Post.objects.filter(user=self.the_user2).count(), 1)

        deleted_post = Post.objects.get(user=self.the_user1, heading='post 2')
        deleted_post.delete()

        self.assertEqual(Post.objects.all().count(), 2)
        self.assertEqual(Post.objects.filter(user=self.the_user1).count(), 1)
        self.assertEqual(Post.objects.filter(user=self.the_user2).count(), 1)

    # ------------------------------------------------------------------------------------------------------------------
    def test_support_messages(self):
        self.assertEqual(SupportMessage.objects.all().count(), 4)
        self.assertEqual(SupportMessage.objects.filter(email='testemail1@mail.co').count(), 2)
        self.assertEqual(SupportMessage.objects.filter(email='test_email22@mail.co').count(), 1)
        self.assertEqual(SupportMessage.objects.filter(is_checked=False).count(), 4)

        checked_message = SupportMessage.objects.get(email='testemail1@mail.co', text='Test text1')
        checked_message.is_checked = True
        checked_message.save()

        self.assertEqual(SupportMessage.objects.filter(is_checked=False).count(), 3)

    # ------------------------------------------------------------------------------------------------------------------
    def tearDown(self):
        for book in Book.objects.all():
            if os.path.exists(book.book_file.path):
                os.remove(book.book_file.path)
            if book.photo and os.path.exists(book.photo.path):
                os.remove(book.photo.path)
