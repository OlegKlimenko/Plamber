# -*- coding: utf-8 -*-

import imghdr
import io
from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError

import PyPDF2

from django.core.exceptions import ValidationError


# ----------------------------------------------------------------------------------------------------------------------
def validate_image(value):
    """
    Validates if the image which is uploading is exactly image, because file can be renamed.
    Raises an error if validation not passed.

    :param str value: The file object.
    """
    if not imghdr.what(value):
        raise ValidationError('Tried to upload not an image!')


# ----------------------------------------------------------------------------------------------------------------------
def validate_book(value):
    """
    Validates the uploading file is a valid FB2/PDF format.

    :param value: The File object.
    """
    validators = {'fb2': validate_fb2(value), 'pdf': validate_pdf(value)}

    if not any(validators.values()):
        raise ValidationError('Tried to upload not FB2/PDF file as a book!')

    # TODO: This will be an issue when epub will be added (They both are XML.)
    return next(key for key in validators if validators[key])


# ----------------------------------------------------------------------------------------------------------------------
def validate_fb2(value):
    try:
        value.seek(0)
        parseString(value.read())
        return True
    except ExpatError:
        return False


# ----------------------------------------------------------------------------------------------------------------------
def validate_pdf(value):
    try:
        value.seek(0)
        PyPDF2.PdfFileReader(io.BytesIO(value.read()))
        return True
    except PyPDF2.utils.PdfReadError:
        return False
