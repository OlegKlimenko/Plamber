# -*- coding: utf-8 -*-

import imghdr
import io

import PyPDF2

from django.core.exceptions import ValidationError


# ----------------------------------------------------------------------------------------------------------------------
def validate_image(value):
    """
    Validates if the image which is uploading is exactly image, because file can be renamed.
    Raises an error if validation not passed.

    :param str value: The path to image.
    """
    if not imghdr.what(value):
        raise ValidationError('Try to upload not an image!')


# ----------------------------------------------------------------------------------------------------------------------
def validate_pdf(value):
    """
    Validates if the uploading file is PDF.
    Raises an error if validation not passed.

    :param value: The document path.
    """
    try:
        PyPDF2.PdfFileReader(io.BytesIO(value.read()))
    except PyPDF2.utils.PdfReadError:
        raise ValidationError('Try to upload not PDF as a book!')
