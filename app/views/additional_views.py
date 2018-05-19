# -*- coding: utf-8 -*-

import logging
from datetime import datetime

from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404, render

from ..models import TheUser

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
