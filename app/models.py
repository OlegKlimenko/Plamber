# -*- coding: utf-8 -*-

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User


# ----------------------------------------------------------------------------------------------------------------------
class TheUser(models.Model):
    id_user = models.OneToOneField(User)
    user_photo = models.ImageField(null=True, blank=True)

    # ------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        return str(self.id_user)


# ----------------------------------------------------------------------------------------------------------------------
class Category(models.Model):
    category_name = models.CharField(max_length=30)

    # ------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        return self.category_name


# ----------------------------------------------------------------------------------------------------------------------
class Author(models.Model):
    author_name = models.CharField(max_length=30)

    # ------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        return self.author_name


# ----------------------------------------------------------------------------------------------------------------------
class Language(models.Model):
    language = models.CharField(max_length=30)

    # ------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        return self.language


# ----------------------------------------------------------------------------------------------------------------------
class Book(models.Model):
    book_name = models.CharField(max_length=30)
    id_author = models.ForeignKey(Author)
    id_category = models.ForeignKey(Category)
    description = models.CharField(max_length=1000, null=True, blank=True)
    language = models.ForeignKey(Language)
    photo = models.ImageField(null=True, blank=True, upload_to='book_media')
    book_file = models.FileField(upload_to='book_media')
    who_added = models.ForeignKey(TheUser)

    # ------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        return "{0}, {1}, язык({2})".format(self.book_name, self.id_author, self.language)


# ----------------------------------------------------------------------------------------------------------------------
class BookRating(models.Model):
    id_user = models.ForeignKey(TheUser)
    id_book = models.ForeignKey(Book)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])


# ----------------------------------------------------------------------------------------------------------------------
class BookComment(models.Model):
    id_user = models.ForeignKey(TheUser)
    id_book = models.ForeignKey(Book)
    text = models.CharField(max_length=500)


# ----------------------------------------------------------------------------------------------------------------------
class AddedBook(models.Model):
    id_user = models.ForeignKey(TheUser)
    id_book = models.ForeignKey(Book)
    last_page = models.PositiveIntegerField(default=1)
