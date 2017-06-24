# -*- coding: utf-8 -*-

import json
import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from ..forms import LogInForm, IsUserExistsForm, IsMailExistsForm, SignInForm, ForgotPasswordForm
from ..models import AddedBook, TheUser
from ..recommend import get_recommend
from ..tasks import restore_account, successful_registration
from ..utils import generate_password, validate_captcha

RANDOM_BOOKS_COUNT = 4

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
def index(request):
    """
    Checks, if request method GET, returns index page. If POST, and all checks are passed, returns home page.

    :param django.core.handlers.wsgi.WSGIRequest request: The request on index page.
    :return: The HTML page.
    """
    if request.method == 'GET':
        if request.user.is_authenticated():
            return home(request)
        else:
            return render(request, 'index.html')

    elif request.method == 'POST':
        return user_login(request)


# ----------------------------------------------------------------------------------------------------------------------
def home(request):
    """
    Returns the 'Home page'.

    :param django.core.handlers.wsgi.WSGIRequest request: The request on index page.
    :return: The 'Home page'.
    """
    books = AddedBook.get_user_added_books(request.user)
    recommend_books = get_recommend(request.user, books, RANDOM_BOOKS_COUNT, [])

    return render(request, 'home.html', {'books': books, 'recommend_books': recommend_books})


# ----------------------------------------------------------------------------------------------------------------------
def user_login(request):
    """
    Checks if user is authenticated.

    :param django.core.handlers.wsgi.WSGIRequest request: The request on index page.
    :return: The 'Index' or 'Home' page.
    """
    log_in_form = LogInForm(request.POST)

    if log_in_form.is_valid():
        user = authenticate(username=log_in_form.cleaned_data['username'],
                            password=log_in_form.cleaned_data['passw'])
        if user:
            login(request, user)
            logger.info("User '{}' logged in.".format(user.username))

            return redirect('index')
        else:
            return render(request, 'index.html', {'invalid_authentication': True})


# ----------------------------------------------------------------------------------------------------------------------
def is_user_exists(request):
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
def is_mail_exists(request):
    """
    Checks if mail is exists. If exists return True, else False.

    :param django.core.handlers.wsgi.WSGIRequest request: The ajax request on index page.
    :return: True or False.
    """
    if request.is_ajax():
        is_mail_exists_form = IsMailExistsForm(request.GET)

        if is_mail_exists_form.is_valid():
            try:
                User.objects.get(email=is_mail_exists_form.cleaned_data['email'])
                return HttpResponse(json.dumps(True), content_type='application/json')
            except ObjectDoesNotExist:
                return HttpResponse(json.dumps(False), content_type='application/json')
    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def sign_in(request):
    """
    Creates a new user and returns page with registration status.

    :param django.core.handlers.wsgi.WSGIRequest request: The request for creating new user.
    :return: The page with registration status.
    """
    if request.method == 'POST':
        sign_in_form = SignInForm(request.POST)

        if sign_in_form.is_valid():
            re_captcha_response = sign_in_form.get('g-recaptcha-response', '')
            
            if validate_captcha(re_captcha_response):
                with transaction.atomic():
                    user = User.objects.create_user(username=sign_in_form.cleaned_data['username'],
                                                    email=sign_in_form.cleaned_data['email'],
                                                    password=sign_in_form.cleaned_data['passw1'])
                    TheUser.objects.create(id_user=user)

                    logger.info("Created user with name: '{}' mail: '{}' and id: '{}'"
                                .format(user.username, user.email, user.id))
                    login(request, user)

                    successful_registration.delay(user.username, user.email)

            return redirect('/')


# ----------------------------------------------------------------------------------------------------------------------
def restore_data(request):
    """
    Restores the password for user.

    :param django.core.handlers.wsgi.WSGIRequest request: The request for restoring password.
    :return: The response about restoring password.
    """
    if request.method == 'POST':
        forgot_form = ForgotPasswordForm(request.POST)

        if forgot_form.is_valid():
            with transaction.atomic():
                temp_password = generate_password()

                user = get_object_or_404(User, email=forgot_form.cleaned_data['email'])
                user.set_password(temp_password)
                user.save()

                restore_account.delay(user.username, temp_password, forgot_form.cleaned_data['email'])

                logger.info("The password for user: '{}' restored successfully.".format(user))

                return HttpResponse(json.dumps(True), content_type='application/json')
