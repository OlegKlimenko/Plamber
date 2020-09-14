# -*- coding: utf-8 -*-

import json
import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from ..constants import Queues
from ..forms import (LogInUsernameForm, LogInEmailForm, IsUserExistsForm, IsMailExistsForm,
                     SignInForm, ForgotPasswordForm)
from ..models import AddedBook, Book
from ..recommend import get_recommend
from ..tasks import restore_account, successful_registration
from ..utils import generate_password, validate_captcha
from ..views import process_method, process_ajax, process_form

RANDOM_BOOKS_COUNT = 6

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
            return render(request, 'index.html', {'books_count': Book.objects.all().count()})

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

    logger.warning("User '{}' tried to login with '{}' password IP: {}".format(
        username, password, request.META.get('REMOTE_ADDR')
    ))
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
@process_ajax(404)
@process_form('GET', IsUserExistsForm, 404)
def is_user_exists(request, form):
    """
    Checks if user is exists. If exists return True, else False.
    """
    try:
        User.objects.get(username=form.cleaned_data['username'])
        return HttpResponse(json.dumps(True), content_type='application/json')

    except ObjectDoesNotExist:
        return HttpResponse(json.dumps(False), content_type='application/json')


# ----------------------------------------------------------------------------------------------------------------------
@process_ajax(404)
@process_form('GET', IsMailExistsForm, 404)
def is_mail_exists(request, form):
    """
    Checks if mail is exists. If exists return True, else False.
    """
    try:
        User.objects.get(email=form.cleaned_data['email'])
        return HttpResponse(json.dumps(True), content_type='application/json')

    except ObjectDoesNotExist:
        return HttpResponse(json.dumps(False), content_type='application/json')


# ----------------------------------------------------------------------------------------------------------------------
@process_method('POST', 404)
def sign_in(request):
    """
    Creates a new user and returns page with registration status.
    """
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

                successful_registration.apply_async(args=(user.username, user.email), queue=Queues.default)

        return redirect('/')

    logger.error("Failed creating new user. username: '{}' email: '{}'".format(
        request.POST.get('username'), request.POST.get('email')
    ))
    return HttpResponse(status=400)


# ----------------------------------------------------------------------------------------------------------------------
@process_method('POST', 404)
@process_form('POST', ForgotPasswordForm, 400)
def restore_data(request, form):
    """
    Restores the password for user.
    """
    with transaction.atomic():
        temp_password = generate_password()

        user = get_object_or_404(User, email=form.cleaned_data['email'])
        user.set_password(temp_password)
        user.save()

        restore_account.apply_async(
            args=(user.username, temp_password, form.cleaned_data['email']), queue=Queues.high_priority
        )
        logger.info("The password for user: '{}' restored successfully.".format(user))

        return HttpResponse(json.dumps(True), content_type='application/json')
