# -*- coding: utf-8 -*-

from django.contrib.staticfiles.templatetags.staticfiles import static

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
    email = serializers.ReadOnlyField(source='id_user.email')
    user_photo = serializers.SerializerMethodField('get_user_photo_url')

    def get_user_photo_url(self, obj):
        return obj.user_photo.url if obj.user_photo else static('/app/images/user.png')


# ----------------------------------------------------------------------------------------------------------------------
class CommentSerializer(serializers.Serializer):
    user = serializers.ReadOnlyField(source='id_user.id_user.username')
    user_photo = serializers.SerializerMethodField('get_user_photo_url')
    text = serializers.CharField(max_length=500)
    posted_date = serializers.DateField()

    def get_user_photo_url(self, obj):
        return obj.id_user.user_photo.url if obj.id_user.user_photo else static('/app/images/user.png')
