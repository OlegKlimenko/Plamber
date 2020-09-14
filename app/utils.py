# -*- coding: utf-8 -*-

import os
import random
import string

import requests
from PIL import Image

from django.conf import settings

PASSWORD_LENGTH = 12


# ----------------------------------------------------------------------------------------------------------------------
def generate_password():
    """
    Generates the random temporary password.

    :rtype str: The new temp password.
    """
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(PASSWORD_LENGTH))


# ----------------------------------------------------------------------------------------------------------------------
def resize_image(path, width):
    """
    Resizes the image.

    :param str path:  The path to the image file.
    :param int width: The width of the output image.
    """
    try:
        img = Image.open(path)

        ratio = width / float(img.width)
        height = int(float(img.height) * float(ratio))

        new_img = img.resize((width, height), Image.ANTIALIAS)
        new_img.save(path)

    except IOError:
        pass


# ----------------------------------------------------------------------------------------------------------------------
def validate_captcha(captcha_post):
    """
    Validates the Google re-captcha data.

    :param str captcha_post: The re-captcha post data
    :return bool:
    """
    validated = False

    data = {
        'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
        'response': captcha_post
    }

    response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data, verify=False).json()
    if response['success']:
        validated = True

    return validated
