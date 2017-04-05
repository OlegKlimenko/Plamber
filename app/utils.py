# -*- coding: utf-8 -*-

import random
import string

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
