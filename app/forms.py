# -*- coding: utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.validators import RegexValidator, EmailValidator

from .validators import validate_image, validate_pdf


# ----------------------------------------------------------------------------------------------------------------------
class IsUserExistsForm(forms.Form):
    username = forms.CharField(max_length=30,
                               validators=[RegexValidator(regex='^[a-zA-Z0-9_]{2,30}')])


# ----------------------------------------------------------------------------------------------------------------------
class IsMailExistsForm(forms.Form):
    email = forms.CharField(max_length=320,
                            validators=[EmailValidator()])


# ----------------------------------------------------------------------------------------------------------------------
class SignInForm(forms.Form):
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
        Checks if two of the passwords are the same. If not, raises an error.
        """
        cleaned_data = super(SignInForm, self).clean()

        if cleaned_data['passw1'] != cleaned_data['passw2']:
            raise ValidationError('Passwords are not matching!')

        if 'admin' in cleaned_data['username']:
            raise ValidationError('Not allowed username!')


# ----------------------------------------------------------------------------------------------------------------------
class LogInForm(forms.Form):
    username = forms.CharField(max_length=30,
                               validators=[RegexValidator(regex='^[a-zA-Z0-9_]{2,30}')])
    passw = forms.CharField(max_length=16)


# ----------------------------------------------------------------------------------------------------------------------
class GenerateAuthorsForm(forms.Form):
    part = forms.CharField(max_length=70)


# ----------------------------------------------------------------------------------------------------------------------
class GenerateBooksForm(forms.Form):
    part = forms.CharField(max_length=150)


# ----------------------------------------------------------------------------------------------------------------------
class AddBookForm(forms.Form):
    bookname = forms.CharField(max_length=150)
    author = forms.CharField(max_length=100)
    category = forms.CharField(max_length=30)
    language = forms.CharField(max_length=30)
    about = forms.CharField(widget=forms.Textarea)
    bookfile = forms.FileField(validators=[validate_pdf])
    private = forms.BooleanField(required=False)


# ----------------------------------------------------------------------------------------------------------------------
class StoreBookImageForm(forms.Form):
    id = forms.IntegerField()
    image = forms.CharField()


# ----------------------------------------------------------------------------------------------------------------------
class BookHomeForm(forms.Form):
    book = forms.IntegerField()


# ----------------------------------------------------------------------------------------------------------------------
class ChangeRatingForm(forms.Form):
    book = forms.IntegerField()
    rating = forms.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])


# ----------------------------------------------------------------------------------------------------------------------
class AddCommentForm(forms.Form):
    book = forms.IntegerField()
    comment = forms.CharField(max_length=500)


# ----------------------------------------------------------------------------------------------------------------------
class SortForm(forms.Form):
    category = forms.IntegerField()
    criterion = forms.CharField(max_length=30)


# ----------------------------------------------------------------------------------------------------------------------
class SearchBookForm(forms.Form):
    data = forms.CharField(max_length=255)


# ----------------------------------------------------------------------------------------------------------------------
class SetCurrentPageForm(forms.Form):
    page = forms.IntegerField()
    book = forms.CharField(max_length=500)


# ----------------------------------------------------------------------------------------------------------------------
class AddBookImageForm(forms.Form):
    book = forms.CharField(max_length=255)
    image = forms.FileField()


# ----------------------------------------------------------------------------------------------------------------------
class UploadAvatarForm(forms.Form):
    avatar = forms.FileField(validators=[validate_image])


# ----------------------------------------------------------------------------------------------------------------------
class ChangePasswordForm(forms.Form):
    prev_password = forms.CharField(max_length=16)
    new_password = forms.CharField(max_length=16)


# ----------------------------------------------------------------------------------------------------------------------
class ForgotPasswordForm(forms.Form):
    email = forms.CharField(max_length=320,
                            validators=[EmailValidator()])
