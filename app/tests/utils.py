# -*- coding: utf-8 -*-

from django.utils.html import escape


# ----------------------------------------------------------------------------------------------------------------------
class Utils:
    """
    Class with util functions which helps to generate some data.
    """

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def generate_sort_dict(book):
        return {
            'id': book.id,
            'name': escape(book.book_name),
            'author': escape(book.id_author.author_name),
            'url': book.photo.url if book.photo else '',
            'upload_date': book.upload_date.strftime('%d-%m-%Y')
        }
