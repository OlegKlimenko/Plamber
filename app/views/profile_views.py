# -*- coding: utf-8 -*-

import json
import logging

from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from ..tasks import changed_password
from app.forms import UploadAvatarForm, ChangePasswordForm
from app.models import TheUser, AddedBook

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
def profile(request, profile_id):
    """
    Renders the profile page.

    :param django.core.handlers.wsgi.WSGIRequest request: The request for looking profile.
    :param int profile_id: The id profile we want to look.
    :return: HTML page.
    """
    if request.method == 'GET':
        if request.user.is_authenticated():
            user = get_object_or_404(User, id=profile_id)
            profile_user = get_object_or_404(TheUser, id_user=user)

            added_books = AddedBook.objects.filter(id_user=profile_user)

            context = {'profile_user': profile_user, 'added_books': added_books}

            if request.user.username == profile_user.id_user.username:
                context['owner'] = True

            return render(request, 'profile.html', context)

        else:
            return redirect('index')
    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def upload_avatar(request):
    """
    Sets new user's avatar.

    :param django.core.handlers.wsgi.WSGIRequest request: The request for upload avatar.
    :return: JSON response
    """
    if request.is_ajax():
        upload_avatar_form = UploadAvatarForm(request.POST, request.FILES)

        with transaction.atomic():
            user = get_object_or_404(User, id=request.user.id)
            profile_user = get_object_or_404(TheUser, id_user=user)

            if upload_avatar_form.is_valid():
                profile_user.user_photo.save('user_{}.png'.format(profile_user.id),
                                             upload_avatar_form.cleaned_data['avatar'])
                profile_user.save()
                logger.info("User '{}' changed his avatar.".format(profile_user))

                response_data = {'message': 'Аватар успешно изменен!'}
                return HttpResponse(json.dumps(response_data), content_type='application/json')

            else:
                logger.info("User '{}' tried to upload not an image as avatar!".format(profile_user))
                return HttpResponse(json.dumps(False), content_type='application/json', status=500)

    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def change_password(request):
    """
    Sets the new password for user.

    :param django.core.handlers.wsgi.WSGIRequest request: The request for changing password.
    :return: JSON response
    """
    if request.is_ajax():
        change_password_form = ChangePasswordForm(request.POST)

        if change_password_form.is_valid():
            with transaction.atomic():

                if request.user.check_password(change_password_form.cleaned_data['prev_password']):
                    request.user.set_password(change_password_form.cleaned_data['new_password'])
                    request.user.save()

                    logger.info("User '{}' changed his password successfully.".format(request.user))

                    changed_password.delay(request.user.username, request.user.email)

                    return HttpResponse(json.dumps('Пароль успешно изменен!'), content_type='application/json')

                else:
                    return HttpResponse(json.dumps('Старый пароль не совпадает. Проверьте на наличие ошибок.'),
                                        content_type='application/json')
    else:
        return HttpResponse(status=404)
