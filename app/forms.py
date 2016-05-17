# -*- coding: utf-8 -*-

from django import forms


# ----------------------------------------------------------------------------------------------------------------------
class IsUserExistsForm(forms.Form):
    username = forms.CharField(max_length=30)


# ----------------------------------------------------------------------------------------------------------------------
class SignInForm(forms.Form):
    username = forms.CharField(max_length=30)
    email = forms.CharField(max_length=320)
    passw1 = forms.CharField(max_length=16)
    passw2 = forms.CharField(max_length=16)


# ----------------------------------------------------------------------------------------------------------------------
class LogInForm(forms.Form):
    username = forms.CharField(max_length=30)
    passw = forms.CharField(max_length=16)


# ----------------------------------------------------------------------------------------------------------------------
class GenerateAuthorsForm(forms.Form):
    author_part = forms.CharField(max_length=70)


# ----------------------------------------------------------------------------------------------------------------------
class AddBookForm(forms.Form):
    bookname = forms.CharField(max_length=70)
    author = forms.CharField(max_length=70)
    category = forms.CharField(max_length=30)
    language = forms.CharField(max_length=30)
    about = forms.CharField(widget=forms.Textarea)
    bookfile = forms.FileField()


# ----------------------------------------------------------------------------------------------------------------------
class BookHomeForm(forms.Form):
    book_id = forms.IntegerField()


# ----------------------------------------------------------------------------------------------------------------------
class ChangeRatingForm(forms.Form):
    book_id = forms.IntegerField()
    rating = forms.IntegerField()


# ----------------------------------------------------------------------------------------------------------------------
class AddCommentForm(forms.Form):
    book_id = forms.IntegerField()
    comment = forms.CharField(max_length=500)
