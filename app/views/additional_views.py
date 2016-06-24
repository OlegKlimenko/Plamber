# -*- coding: utf-8 -*-

from django.contrib.auth import logout
from django.shortcuts import render
from django.shortcuts import redirect


# ----------------------------------------------------------------------------------------------------------------------
def thanks_view(request):
    """
    Returns a page with success registration message.

    :param django.core.handlers.wsgi.WSGIRequest request: The request for generating a success register page.
    :return: The page with info about success registration.
    """
    return render(request, 'register_success.html')


# ----------------------------------------------------------------------------------------------------------------------
def user_logout_view(request):
    """
    Closes session, returns index page.

    :param django.core.handlers.wsgi.WSGIRequest request: The request for log out.
    :return: Index page.
    """
    logout(request)
    return redirect('index')
