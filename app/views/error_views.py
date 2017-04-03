# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext


# ----------------------------------------------------------------------------------------------------------------------
def error_output(request, code):
    """
    Returns the HTML page as output on error, depending on the code.

    :param django.core.handlers.wsgi.WSGIRequest request:
    :param int                                   code:    Status code number
    :return: HTML page.
    """
    response = render_to_response('error_status_page.html',
                                  context=RequestContext(request, {'status_code': code}))
    response.status_code = code
    return response


# ----------------------------------------------------------------------------------------------------------------------
def not_found_404(request):
    """
    'Page not found' request handler.

    :param django.core.handlers.wsgi.WSGIRequest request:
    :return: HTML page.
    """
    return error_output(request, 404)


# ----------------------------------------------------------------------------------------------------------------------
def bad_request_400(request):
    """
    'Bad request' request handler.

    :param django.core.handlers.wsgi.WSGIRequest request:
    :return: HTML page.
    """
    return error_output(request, 400)


# ----------------------------------------------------------------------------------------------------------------------
def permission_denied_403(request):
    """
    'Permission denied' request handler.

    :param django.core.handlers.wsgi.WSGIRequest request:
    :return: HTML page.
    """
    return error_output(request, 403)


# ----------------------------------------------------------------------------------------------------------------------
def internal_error_500(request):
    """
    'Internal server error' request handler.

    :param django.core.handlers.wsgi.WSGIRequest request:
    :return: HTML page.
    """
    return error_output(request, 500)
