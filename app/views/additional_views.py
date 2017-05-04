# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponse
from django.shortcuts import redirect

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
def user_logout(request):
    """
    Closes session, returns index page.

    :param django.core.handlers.wsgi.WSGIRequest request: The request for log out.
    :return: Index page.
    """
    logger.info("User '{}' logged out.".format(request.user))

    logout(request)
    return redirect('index')


# ----------------------------------------------------------------------------------------------------------------------
def verification_token(request, file):
    """
    Handles the request for SSL token.

    :param django.core.handlers.wsgi.WSGIRequest request: The request for SSL checking.
    :param str                                   file:    The filename which we want to return
    :return str: Plain text as output
    """
    with open(settings.BASE_DIR + '/Plamber/{}'.format(file), 'r') as data:
        return HttpResponse(data.read(), content_type='text/plain')
