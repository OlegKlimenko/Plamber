# -*- coding: utf-8 -*-

import os
import random
import string
import subprocess

import PyPDF2
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
def compress_pdf(old_path):
    """
    Compresses the PDF file and replace with old one if compression was success.

    :param str old_path: The path to file which we will compress.

    :return bool: The status.
    """
    old_filename, old_file_ext = os.path.splitext(old_path)
    new_path = old_filename + 'compressed' + old_file_ext

    compress = subprocess.Popen([
        '/usr/bin/gs',
        '-sDEVICE=pdfwrite',
        '-dCompatibilityLevel=1.4',
        '-dPDFSETTINGS=/screen',
        '-dEmbedAllFonts=true',
        '-dColorImageResolution=150',
        '-dGrayImageResolution=600',
        '-dMonoImageResolution=1200',
        '-dNOPAUSE',
        '-dBATCH',
        '-dQUIET',
        '-sOutputFile={}'.format(new_path),
        old_path
    ], stdout=subprocess.PIPE)

    if compress.communicate():
        old_file_size = os.stat(old_path).st_size
        new_file_size = os.stat(new_path).st_size

        if new_file_size < old_file_size:
            # If the size changed, check if is a correct PDF. If yes, replace with compressed one.
            # If no, leave old one, and remove compressed.
            try:
                PyPDF2.PdfFileReader(new_path)

                os.remove(old_path)
                os.rename(new_path, old_path)

            except PyPDF2.utils.PdfReadError:
                os.remove(new_path)
        else:
            os.remove(new_path)

        return True


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
