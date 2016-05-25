# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import RequestContext, loader

from app.models import Category


# ----------------------------------------------------------------------------------------------------------------------
def categories_view(request):
    """
    Returns page with book categories.

    :param django.core.handlers.wsgi.WSGIRequest request: The request on categories page.
    :return: The HTML page.
    """
    if request.method == "GET":
        if request.user.is_authenticated():
            categories = Category.objects.all()

            template = loader.get_template('categories.html')
            context = RequestContext(request, {'categories': categories})
            return HttpResponse(template.render(context))
        else:
            return redirect('index')


# ----------------------------------------------------------------------------------------------------------------------
def selected_category_view(request, id):
    """
    Returns page with selected category.

    :param django.core.handlers.wsgi.WSGIRequest request: The request on selected category page.
    :param str id: The identifier of a category.
    :return: The HTML page.
    """
    if request.method == 'GET':
        if request.user.is_authenticated():
            template = loader.get_template('selected_category.html')
            context = RequestContext(request, {})
            return HttpResponse(template.render(context))
        else:
            return redirect('index')