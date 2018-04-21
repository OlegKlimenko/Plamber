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
    """
    if request.method == 'POST':
        logger.info("User '{}' logged out.".format(request.user))

        logout(request)
        return redirect('index')

    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def share_txt(request, file):
    """
    Returns the shared .txt files.
    """
    with open(settings.BASE_DIR + '/Plamber/additional/{}'.format(file), 'r') as data:
        return HttpResponse(data.read(), content_type='text/plain')


# ----------------------------------------------------------------------------------------------------------------------
def share_xml(request, file):
    """
    Returns the shared .xml files.
    """
    with open(settings.BASE_DIR + '/Plamber/additional/{}'.format(file), 'r') as data:
        return HttpResponse(data.read(), content_type='application/xml')
