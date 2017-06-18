# -*- coding: utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.validators import RegexValidator, EmailValidator

from .validators import validate_image, validate_pdf


# ----------------------------------------------------------------------------------------------------------------------
class IsUserExistsForm(forms.Form):
    """
    Class for form if user is exists.
    """
    username = forms.CharField(max_length=30,
                               validators=[RegexValidator(regex='^[a-zA-Z0-9_]{2,30}')])


# ----------------------------------------------------------------------------------------------------------------------
class IsMailExistsForm(forms.Form):
    """
    Class for form if mail is exists.
    """
    email = forms.CharField(max_length=320,
                            validators=[EmailValidator()])


# ----------------------------------------------------------------------------------------------------------------------
class SignInForm(forms.Form):
    """
    Class for creating new user form.
    """
    username = forms.CharField(max_length=30,
                               validators=[RegexValidator(regex='^[a-zA-Z0-9_]{2,30}'),
                                           MinLengthValidator(2),
                                           MaxLengthValidator(30)])
    email = forms.CharField(max_length=320,
                            validators=[EmailValidator()])
    passw1 = forms.CharField(max_length=16,
                             validators=[MinLengthValidator(6),
                                         MaxLengthValidator(16)])
    passw2 = forms.CharField(max_length=16,
                             validators=[MinLengthValidator(6),
                                         MaxLengthValidator(16)])

    def clean(self):
        """
        Checks if two of the passwords are the same. If not. Raises an error.
        """
        cleaned_data = super(SignInForm, self).clean()

        if cleaned_data['passw1'] != cleaned_data['passw2']:
            raise ValidationError('Passwords are not matching!')


# ----------------------------------------------------------------------------------------------------------------------
class LogInForm(forms.Form):
    """
    Class for login form.
    """
    username = forms.CharField(max_length=30,
                               validators=[RegexValidator(regex='^[a-zA-Z0-9_]{2,30}')])
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
    bookname = forms.CharField(max_length=150)
    author = forms.CharField(max_length=100)
    category = forms.CharField(max_length=30)
    language = forms.CharField(max_length=30)
    about = forms.CharField(widget=forms.Textarea)
    bookfile = forms.FileField(validators=[validate_pdf])


# ----------------------------------------------------------------------------------------------------------------------
class StoreBookImageForm(forms.Form):
    """
    Class for storing book image.
    """
    id = forms.IntegerField()
    image = forms.CharField()


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
    rating = forms.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])


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


# ----------------------------------------------------------------------------------------------------------------------
class UploadAvatarForm(forms.Form):
    """
    Form for uploading user's avatar.
    """
    avatar = forms.FileField(validators=[validate_image])


# ----------------------------------------------------------------------------------------------------------------------
class ChangePasswordForm(forms.Form):
    """
    Form for changing user's password.
    """
    prev_password = forms.CharField(max_length=16)
    new_password = forms.CharField(max_length=16)


# ----------------------------------------------------------------------------------------------------------------------
class ForgotPasswordForm(forms.Form):
    """
    Form for checking the mail for password recovery.
    """
    email = forms.CharField(max_length=320,
                            validators=[EmailValidator()])
