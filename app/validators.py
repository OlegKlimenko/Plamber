# -*- coding: utf-8 -*-

import imghdr

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
