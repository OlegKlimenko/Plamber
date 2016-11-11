# -*- coding: utf-8 -*-

import json
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render, redirect

from ..forms import LogInForm, IsUserExistsForm, SignInForm
from ..models import AddedBook, TheUser


# ----------------------------------------------------------------------------------------------------------------------
def index_view(request):
    """
    Checks, if request method GET, returns index page. If POST, and all checks are passed, returns home page.

    :param django.core.handlers.wsgi.WSGIRequest request: The request on index page.
    :return: The HTML page.
    """
    if request.method == 'GET':
        if request.user.is_authenticated():
            return home_view(request)
        else:
            return render(request, 'index.html')

    elif request.method == 'POST':
        return login_view(request)


# ----------------------------------------------------------------------------------------------------------------------
def home_view(request):
    """
    Returns the 'Home page'.

    :param django.core.handlers.wsgi.WSGIRequest request: The request on index page.
    :return: The 'Home page'.
    """
    books = []
    added_books = AddedBook.objects.filter(id_user=TheUser.objects.get(id_user=request.user))

    for added_book in added_books:
        books.append(added_book.id_book)

    template = loader.get_template('home.html')
    context = RequestContext(request, {'books': books})
    return HttpResponse(template.render(context))


# ----------------------------------------------------------------------------------------------------------------------
def login_view(request):
    """
    Checks if user is authenticated.

    :param django.core.handlers.wsgi.WSGIRequest request: The request on index page.
    :return: The 'Index' or 'Home' page.
    """
    log_in_form = LogInForm(request.POST)

    if log_in_form.is_valid():
        user = authenticate(username=log_in_form.cleaned_data['username'],
                            password=log_in_form.cleaned_data['passw'])

        # If user not authenticated returns None.
        if user:
            login(request, user)
            return redirect('index')
        else:
            template = loader.get_template('index.html')
            context = RequestContext(request, {'invalid_authentication': True})
            return HttpResponse(template.render(context))


# ----------------------------------------------------------------------------------------------------------------------
def is_user_exists_view(request):
    """
    Checks if user is exists. If exists return True, else False.

    :param django.core.handlers.wsgi.WSGIRequest request: The ajax request on index page.
    :return: True or False.
    """
    if request.is_ajax():
        is_user_exists_form = IsUserExistsForm(request.GET)

        if is_user_exists_form.is_valid():
            try:
                User.objects.get(username=is_user_exists_form.cleaned_data['username'])
                return HttpResponse(json.dumps(True), content_type='application/json')
            except ObjectDoesNotExist:
                return HttpResponse(json.dumps(False), content_type='application/json')
    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def sign_in_view(request):
    """
    Creates a new user and returns page with registration status.

    :param django.core.handlers.wsgi.WSGIRequest request: The request for creating new user.
    :return: The page with registration status.
    """
    if request.method == 'POST':
        sign_in_form = SignInForm(request.POST)

        if sign_in_form.is_valid():
            with transaction.atomic():
                user = User.objects.create_user(
                    username=sign_in_form.cleaned_data['username'],
                    email=sign_in_form.cleaned_data['email'],
                    password=sign_in_form.cleaned_data['passw1'])
                TheUser.objects.create(id_user=user)

                return redirect('/thanks/')
