# -*- coding: utf-8 -*-

import json
import logging
import random

from django.conf import settings
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.html import escape

from ..constants import Queues
from ..forms import UploadAvatarForm, ChangePasswordForm, BookPagingForm
from ..models import AddedBook, Book, TheUser
from ..tasks import changed_password
from ..utils import resize_image

AVATAR_WIDTH = 250

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
def profile(request, profile_id):
    """
    Renders the profile page.
    """
    if request.method == 'GET':
        if request.user.is_authenticated():
            user = get_object_or_404(User, id=profile_id)
            profile_user = get_object_or_404(TheUser, id_user=user)

            added_books = AddedBook.objects.filter(id_user=profile_user)
            uploaded_books = Book.objects.filter(who_added=profile_user).order_by('-id')

            paginator = Paginator(uploaded_books, settings.BOOKS_PER_PAGE)
            page = paginator.page(1)

            context = {
                'profile_user': profile_user,
                'added_books': added_books,
                'uploaded_books': page.object_list,
                'uploaded_books_count': uploaded_books.count(),
                'has_next': page.has_next(),
                'img_random': random.randint(0, 1000)
            }

            if request.user.username == profile_user.id_user.username:
                context['owner'] = True

            return render(request, 'profile.html', context)

        else:
            return redirect('index')
    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def load_uploaded_books(request, profile_id):
    """
    Loads uploaded books on profile page with pagination.
    """
    if request.method == 'GET':
        form = BookPagingForm(request.GET)

        if form.is_valid():
            profile_user = get_object_or_404(TheUser, id=profile_id)
            uploaded_books = Book.objects.filter(who_added=profile_user).order_by('-id')

            paginator = Paginator(uploaded_books, settings.BOOKS_PER_PAGE)
            page = paginator.page(form.cleaned_data['page'])

            books = Book.generate_books(page.object_list)
            for book in books:
                book['name'] = escape(book['name'])
                book['author'] = escape(book['author'])

            response = {
                'profile_id': profile_id,
                'books': books,
                'has_next': page.has_next(),
                'next_page': page.next_page_number() if page.has_next() else paginator.num_pages
            }
            return HttpResponse(json.dumps(response), content_type='application/json')
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def upload_avatar(request):
    """
    Sets new user's avatar.
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

                resize_image(profile_user.user_photo.path, AVATAR_WIDTH)
                logger.info("Image '{}' successfully resized!".format(profile_user.user_photo.path))

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
    """
    if request.is_ajax():
        change_password_form = ChangePasswordForm(request.POST)

        if change_password_form.is_valid():
            with transaction.atomic():
                if request.user.check_password(change_password_form.cleaned_data['prev_password']):
                    request.user.set_password(change_password_form.cleaned_data['new_password'])
                    request.user.save()

                    logger.info("User '{}' changed his password successfully.".format(request.user))
                    changed_password.apply_async(
                        args=(request.user.username, request.user.email), queue=Queues.high_priority
                    )

                    return HttpResponse(json.dumps('Пароль успешно изменен!'), content_type='application/json')

                else:
                    return HttpResponse(json.dumps('Старый пароль не совпадает. Проверьте на наличие ошибок.'),
                                        content_type='application/json')
        return HttpResponse(status=400)

    else:
        return HttpResponse(status=404)
