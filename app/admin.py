# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Category, Author, Book, BookRating, BookComment, AddedBook, TheUser, Language, Post


# ----------------------------------------------------------------------------------------------------------------------
class TheUserAdmin(admin.ModelAdmin):
    """
    Class for pretty representation data of users in admin panel.
    """
    list_display = ('id', 'get_username', 'get_email')

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_username(obj):
        return obj.id_user.username

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_email(obj):
        return obj.id_user.email


# ----------------------------------------------------------------------------------------------------------------------
class CategoryAdmin(admin.ModelAdmin):
    """
    Class for pretty representation data of categories in admin panel.
    """
    list_display = ('category_name',)


# ----------------------------------------------------------------------------------------------------------------------
class AuthorAdmin(admin.ModelAdmin):
    """
    Class for pretty representation data of authors in admin panel.
    """
    list_display = ('author_name',)


# ----------------------------------------------------------------------------------------------------------------------
class LanguageAdmin(admin.ModelAdmin):
    """
    Class for pretty representation data of languages in admin panel.
    """
    list_display = ('language',)


# ----------------------------------------------------------------------------------------------------------------------
class BookAdmin(admin.ModelAdmin):
    """
    Class for pretty representation data of books in admin panel.
    """
    list_display = ('book_name', 'get_author', 'get_category', 'get_language')

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_author(obj):
        return obj.id_author.author_name

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_category(obj):
        return obj.id_category.category_name

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_language(obj):
        return obj.language.language


# ----------------------------------------------------------------------------------------------------------------------
class BookGeneral(admin.ModelAdmin):
    """
    General class for Ratings, Comments and Added books.
    """
    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_user(obj):
        return obj.id_user

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_book(obj):
        return obj.id_book


# ----------------------------------------------------------------------------------------------------------------------
class BookRatingAdmin(BookGeneral):
    """
    Class for pretty representation data of book rating in admin panel.
    """
    list_display = ('get_user', 'get_book', 'rating')


# ----------------------------------------------------------------------------------------------------------------------
class BookCommentAdmin(BookGeneral):
    """
    Class for pretty representation data of book comments in admin panel.
    """
    list_display = ('get_user', 'get_book', 'text')


# ----------------------------------------------------------------------------------------------------------------------
class AddedBookAdmin(BookGeneral):
    """
    Class for pretty representation data of added books in admin panel.
    """
    list_display = ('get_user', 'get_book', 'last_page')


# ----------------------------------------------------------------------------------------------------------------------
class PostAdmin(admin.ModelAdmin):
    """
    Class for pretty representation data of project blog posts in admin panel.
    """
    list_display = ('heading', 'user', 'posted_date')


admin.site.register(TheUser, TheUserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(BookRating, BookRatingAdmin)
admin.site.register(BookComment, BookCommentAdmin)
admin.site.register(AddedBook, AddedBookAdmin)
admin.site.register(Post, PostAdmin)
