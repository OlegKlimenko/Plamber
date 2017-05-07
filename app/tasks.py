# -*- coding: utf-8 -*-

import logging

from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .utils import compress_pdf

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
@shared_task
def restore_account(username, temp_password, recipient):
    """
    Celery task for sending mail on restore user data.

    :param str username:       The restored username.
    :param str temp_password:  The temporary password for restored username.
    :param str recipient:      The mail recipient.
    """
    html_content = render_to_string('mails/account_restore.html', {'username': username, 'password': temp_password})
    text_content = strip_tags(html_content)
    subject = 'Восстановление аккаунта'

    email = EmailMultiAlternatives(subject, text_content, to=[recipient])
    email.attach_alternative(html_content, 'text/html')
    email.send()


# ----------------------------------------------------------------------------------------------------------------------
@shared_task
def changed_password(username, recipient):
    """
    Celery task for sending mail, to notify user about password changed.

    :param str username:   The restored username.
    :param str recipient:  The mail recipient.
    """
    html_content = render_to_string('mails/password_changed.html', {'username': username})
    text_content = strip_tags(html_content)
    subject = 'Изменение пароля аккаунта'

    email = EmailMultiAlternatives(subject, text_content, to=[recipient])
    email.attach_alternative(html_content, 'text/html')
    email.send()


# ----------------------------------------------------------------------------------------------------------------------
@shared_task
def compress_pdf_task(filename):
    """
    Celery task for compressing the PDF file.

    :param str filename: The file name of document which will be compressed.
    """
    logger.info("Started compressing book with name: {}".format(filename))

    compress_pdf(filename)

    logger.info("Book with id: '{}' compressed successfully!".format(filename))
