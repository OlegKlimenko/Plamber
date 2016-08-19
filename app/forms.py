# -*- coding: utf-8 -*-

from django import forms


# ----------------------------------------------------------------------------------------------------------------------
class IsUserExistsForm(forms.Form):
    """
    Class for form if user is exists.
    """
    username = forms.CharField(max_length=30)


# ----------------------------------------------------------------------------------------------------------------------
class SignInForm(forms.Form):
    """
    Class for creating new user form.
    """
    username = forms.CharField(max_length=30)
    email = forms.CharField(max_length=320)
    passw1 = forms.CharField(max_length=16)
    passw2 = forms.CharField(max_length=16)


# ----------------------------------------------------------------------------------------------------------------------
class LogInForm(forms.Form):
    """
    Class for login form.
    """
    username = forms.CharField(max_length=30)
    passw = forms.CharField(max_length=16)


# ----------------------------------------------------------------------------------------------------------------------
class GenerateAuthorsForm(forms.Form):
    """
    Class for form of generating authors of special criterion.
    """
    part = forms.CharField(max_length=70)


# ----------------------------------------------------------------------------------------------------------------------
class AddBookForm(forms.Form):
    """
    Class for adding book form.
    """
    bookname = forms.CharField(max_length=70)
    author = forms.CharField(max_length=70)
    category = forms.CharField(max_length=30)
    language = forms.CharField(max_length=30)
    about = forms.CharField(widget=forms.Textarea)
    bookfile = forms.FileField()


# ----------------------------------------------------------------------------------------------------------------------
class BookHomeForm(forms.Form):
    """
    Class for form adding and removing book from own library.
    """
    book = forms.IntegerField()


# ----------------------------------------------------------------------------------------------------------------------
class ChangeRatingForm(forms.Form):
    """
    Class for changing rating of book form.
    """
    book = forms.IntegerField()
    rating = forms.IntegerField()


# ----------------------------------------------------------------------------------------------------------------------
class AddCommentForm(forms.Form):
    """
    Class for adding comment of book form.
    """
    book = forms.IntegerField()
    comment = forms.CharField(max_length=500)


# ----------------------------------------------------------------------------------------------------------------------
class SortForm(forms.Form):
    """
    Class for form in sorting books.
    """
    category = forms.IntegerField()
    criterion = forms.CharField(max_length=30)


# ----------------------------------------------------------------------------------------------------------------------
class SearchBookForm(forms.Form):
    """
    Class for form in searching books.
    """
    data = forms.CharField(max_length=255)


# ----------------------------------------------------------------------------------------------------------------------
class SetCurrentPageForm(forms.Form):
    """
    Class for changing readed page information form.
    """
    page = forms.IntegerField()
    book = forms.CharField(max_length=500)


# ----------------------------------------------------------------------------------------------------------------------
class AddBookImageForm(forms.Form):
    """
    Class for adding image to a book form.
    """
    book = forms.CharField(max_length=255)
    image = forms.FileField()
