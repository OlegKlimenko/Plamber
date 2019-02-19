# -*- coding: utf-8 -*-

import json
import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from ..forms import (LogInUsernameForm, LogInEmailForm, IsUserExistsForm, IsMailExistsForm,
                     SignInForm, ForgotPasswordForm)
from ..models import AddedBook
from ..recommend import get_recommend
from ..tasks import restore_account, successful_registration
from ..utils import generate_password, validate_captcha

RANDOM_BOOKS_COUNT = 4

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
def index(request):
    """
    Checks, if request method GET, returns index page. If POST, and all checks are passed, returns home page.
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
    """
    books = AddedBook.get_user_added_books(request.user)
    recommend_books = get_recommend(request.user, books, RANDOM_BOOKS_COUNT, [])

    return render(request, 'home.html', {'books': books, 'recommend_books': recommend_books})


# ----------------------------------------------------------------------------------------------------------------------
def login_response(request, username, password):
    """
    Authenticates user and redirects with the appropriate state.
    """
    user = authenticate(username=username, password=password)

    if user:
        login(request, user)
        logger.info("User '{}' logged in.".format(user.username))

        return redirect('index')
    return render(request, 'index.html', {'invalid_authentication': True})


# ----------------------------------------------------------------------------------------------------------------------
def user_login(request):
    """
    Validates request data and logs user.
    """
    email_form = LogInEmailForm(request.POST)
    username_form = LogInUsernameForm(request.POST)

    if email_form.is_valid():
        user_obj = User.objects.filter(email=email_form.cleaned_data['username'])
        username = user_obj[0] if len(user_obj) else None

        return login_response(request, username, email_form.cleaned_data['passw'])

    elif username_form.is_valid():
        return login_response(request, username_form.cleaned_data['username'], username_form.cleaned_data['passw'])

    return render(request, 'index.html', {'invalid_authentication': True})


# ----------------------------------------------------------------------------------------------------------------------
def is_user_exists(request):
    """
    Checks if user is exists. If exists return True, else False.
    """
    if request.is_ajax():
        is_user_exists_form = IsUserExistsForm(request.GET)

        if is_user_exists_form.is_valid():
            try:
                User.objects.get(username=is_user_exists_form.cleaned_data['username'])
                return HttpResponse(json.dumps(True), content_type='application/json')

            except ObjectDoesNotExist:
                return HttpResponse(json.dumps(False), content_type='application/json')

        return HttpResponse(status=404)
    return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def is_mail_exists(request):
    """
    Checks if mail is exists. If exists return True, else False.
    """
    if request.is_ajax():
        is_mail_exists_form = IsMailExistsForm(request.GET)

        if is_mail_exists_form.is_valid():
            try:
                User.objects.get(email=is_mail_exists_form.cleaned_data['email'])
                return HttpResponse(json.dumps(True), content_type='application/json')

            except ObjectDoesNotExist:
                return HttpResponse(json.dumps(False), content_type='application/json')

        return HttpResponse(status=404)
    return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def sign_in(request):
    """
    Creates a new user and returns page with registration status.
    """
    if request.method == 'POST':
        sign_in_form = SignInForm(request.POST)

        if sign_in_form.is_valid():
            re_captcha_response = request.POST.get('g-recaptcha-response', '')

            if validate_captcha(re_captcha_response):
                with transaction.atomic():
                    user = User.objects.create_user(username=sign_in_form.cleaned_data['username'],
                                                    email=sign_in_form.cleaned_data['email'],
                                                    password=sign_in_form.cleaned_data['passw1'])

                    logger.info("Created user with name: '{}' mail: '{}' and id: '{}'"
                                .format(user.username, user.email, user.id))
                    login(request, user)

                    successful_registration.delay(user.username, user.email)

            return redirect('/')
        return HttpResponse(status=400)
    return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def restore_data(request):
    """
    Restores the password for user.
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

        return HttpResponse(status=400)
    return HttpResponse(status=404)
