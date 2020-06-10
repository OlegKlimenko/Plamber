# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime

from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404, render

from ..models import TheUser
from ..views import process_method

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
@process_method('POST', 404)
def user_logout(request):
    """
    Closes session, returns index page.
    """
    logger.info("User '{}' logged out.".format(request.user))
    logout(request)
    return redirect('index')


# ----------------------------------------------------------------------------------------------------------------------
def share_txt(request, file):
    """
    Returns the shared .txt files.
    """
    path = settings.BASE_DIR + '/Plamber/additional/{}'.format(file)

    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as data:
            return HttpResponse(data.read(), content_type='text/plain')

    return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------      
def share_xml(request, file):
    """
    Returns the shared .xml files.
    """
    path = settings.BASE_DIR + '/Plamber/additional/{}'.format(file)

    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as data:
            return HttpResponse(data.read(), content_type='application/xml')

    return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def unsubscribe(request, token):
    """
    Removes the user from the list of blog subscribers.
    """
    username, date = token.split('-')
    user = get_object_or_404(TheUser, id_user__username=username,
                             id_user__date_joined=datetime.fromtimestamp(float(date)))
    user.subscription = False
    user.save()

    return render(request, 'additional/unsubscribe.html', context={'user': user})


# ----------------------------------------------------------------------------------------------------------------------
def payment_success(request):
    """
    Renders status page after donation passed successfully."
    """
    return render(request, 'payment_success.html')
