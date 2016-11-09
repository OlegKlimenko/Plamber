# -*- coding: utf-8 -*-


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
