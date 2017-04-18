# -*- coding: utf-8 -*-

import os
import random
import string
import subprocess

import PyPDF2

PASSWORD_LENGTH = 12


# ----------------------------------------------------------------------------------------------------------------------
def html_escape(text):
    """
    Returns a string with special characters converted to HTML entities.

    :param str text: The string with optionally special characters.

    :rtype str:
    """
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")

    text = text.replace('"', "&quot;")
    text = text.replace('\'', "&#x27;")

    return text


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
