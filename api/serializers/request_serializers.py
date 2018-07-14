# -*- coding: utf-8 -*-

from django.core.validators import MinValueValidator, MaxValueValidator

from rest_framework import serializers


# ----------------------------------------------------------------------------------------------------------------------
class TokenSerializer(serializers.Serializer):
    """
    Parent class for request serializers with user token field which uses in almost all requests.
    """
    user_token = serializers.UUIDField()


# ----------------------------------------------------------------------------------------------------------------------
class UsernameSerializer(serializers.Serializer):
    """
    Parent class for request serializers with username field.
    """
    username = serializers.RegexField('^[a-zA-Z0-9_]*$',
                                      min_length=2,
                                      max_length=30)


# ----------------------------------------------------------------------------------------------------------------------
class EmailSerializer(serializers.Serializer):
    """
    Parent class for request serializers with email field.
    """
    email = serializers.EmailField()


# ----------------------------------------------------------------------------------------------------------------------
class SaveSupportMessageRequest(EmailSerializer):
    text = serializers.CharField(max_length=5000)


# ----------------------------------------------------------------------------------------------------------------------
class HomeRequest(TokenSerializer):
    pass


# ----------------------------------------------------------------------------------------------------------------------
class UserLoginRequest(UsernameSerializer):
    password = serializers.CharField(max_length=16)


# ----------------------------------------------------------------------------------------------------------------------
class RestoreDataRequest(EmailSerializer):
    pass


# ----------------------------------------------------------------------------------------------------------------------
class UserExistsRequest(UsernameSerializer):
    pass


# ----------------------------------------------------------------------------------------------------------------------
class EmailExistsRequest(EmailSerializer):
    pass


# ----------------------------------------------------------------------------------------------------------------------
class SignInRequest(UsernameSerializer, EmailSerializer):
    passw1 = serializers.CharField(min_length=6,
                                   max_length=16)


# ----------------------------------------------------------------------------------------------------------------------
class AllCategoriesRequest(TokenSerializer):
    pass


# ----------------------------------------------------------------------------------------------------------------------
class SelectedCategoryRequest(TokenSerializer):
    category_id = serializers.IntegerField()
    page = serializers.IntegerField(validators=[MinValueValidator(1)])


# ----------------------------------------------------------------------------------------------------------------------
class FindBookRequest(TokenSerializer):
    search_term = serializers.CharField(max_length=255)
    page = serializers.IntegerField(validators=[MinValueValidator(1)])


# ----------------------------------------------------------------------------------------------------------------------
class ProfileRequest(TokenSerializer):
    pass


# ----------------------------------------------------------------------------------------------------------------------
class ChangePasswordRequest(TokenSerializer):
    prev_password = serializers.CharField(min_length=6,
                                          max_length=16)
    new_password = serializers.CharField(min_length=6,
                                         max_length=16)


# ----------------------------------------------------------------------------------------------------------------------
class UploadAvatarRequest(TokenSerializer):
    pass


# ----------------------------------------------------------------------------------------------------------------------
class OpenBookRequest(TokenSerializer):
    book_id = serializers.IntegerField(validators=[MinValueValidator(1)])


# ----------------------------------------------------------------------------------------------------------------------
class SetCurrentPageRequest(TokenSerializer):
    book_id = serializers.IntegerField(validators=[MinValueValidator(1)])
    current_page = serializers.IntegerField(validators=[MinValueValidator(1)])


# ----------------------------------------------------------------------------------------------------------------------
class SelectedBookRequest(TokenSerializer):
    book_id = serializers.IntegerField(validators=[MinValueValidator(1)])


# ----------------------------------------------------------------------------------------------------------------------
class ChangeRatingRequest(TokenSerializer):
    book_id = serializers.IntegerField(validators=[MinValueValidator(1)])
    rating = serializers.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])


# ----------------------------------------------------------------------------------------------------------------------
class AddCommentRequest(TokenSerializer):
    book_id = serializers.IntegerField(validators=[MinValueValidator(1)])
    text = serializers.CharField(max_length=500)


# ----------------------------------------------------------------------------------------------------------------------
class GenerateAuthorsRequest(TokenSerializer):
    author_part = serializers.CharField(max_length=100)


# ----------------------------------------------------------------------------------------------------------------------
class GenerateBooksRequest(TokenSerializer):
    book_part = serializers.CharField(max_length=150)


# ----------------------------------------------------------------------------------------------------------------------
class GenerateLanguagesRequest(TokenSerializer):
    pass


# ----------------------------------------------------------------------------------------------------------------------
class UploadBookRequest(TokenSerializer):
    book_name = serializers.CharField(max_length=150)
    author = serializers.CharField(max_length=100)
    category = serializers.CharField(max_length=30)
    about = serializers.CharField(max_length=1000)
    language = serializers.CharField(max_length=30)


# ----------------------------------------------------------------------------------------------------------------------
class GetReminderRequest(TokenSerializer):
    pass


# ----------------------------------------------------------------------------------------------------------------------
class UpdateReminderRequest(TokenSerializer):
    field = serializers.CharField(max_length=16)
    value = serializers.BooleanField()
