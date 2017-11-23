# -*- coding: utf-8 -*-

from rest_framework import serializers


# ----------------------------------------------------------------------------------------------------------------------
class BookSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    book_name = serializers.CharField(max_length=150)
    id_author = serializers.ReadOnlyField(source='id_author.author_name')
    id_category = serializers.ReadOnlyField(source='id_category.category_name')
    description = serializers.CharField(max_length=1000)
    language = serializers.ReadOnlyField(source='language.language')
    photo = serializers.ImageField()
    book_file = serializers.FileField()
    who_added = serializers.ReadOnlyField(source='who_added.id_user.username')
    upload_date = serializers.DateTimeField()
    private_book = serializers.BooleanField()


# ----------------------------------------------------------------------------------------------------------------------
class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    category_name = serializers.CharField(max_length=150)


# ----------------------------------------------------------------------------------------------------------------------
class ProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.ReadOnlyField(source='id_user.username')
    user_photo = serializers.ImageField()


# ----------------------------------------------------------------------------------------------------------------------
class CommentSerializer(serializers.Serializer):
    user = serializers.ReadOnlyField(source='id_user.id_user.username')
    user_photo = serializers.ReadOnlyField(source='id_user.user_photo.url')
    text = serializers.CharField(max_length=500)
    posted_date = serializers.DateField()
