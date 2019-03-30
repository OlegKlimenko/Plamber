# -*- coding: utf-8 -*-

import time
import logging

from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls.exceptions import NoReverseMatch
from django.utils.html import strip_tags

from .utils import compress_pdf
from .models import TheUser

DAY_IN_SECONDS = 86400

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
@shared_task
def successful_registration(username, recipient):
    """
    Celery task for sending welcome mail after creating new user.

    :param str username:   The restored username.
    :param str recipient:  The mail recipient.
    """
    html_content = render_to_string('mails/registration_success.html', {'username': username})
    text_content = strip_tags(html_content)
    subject = 'Успешная регистрация на plamber.com.ua'

    email = EmailMultiAlternatives(subject, text_content, to=[recipient])
    email.attach_alternative(html_content, 'text/html')
    email.send()


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
def compress_pdf_task(filename, book_id):
    """
    Celery task for compressing the PDF file.

    :param str filename: The file name of document which will be compressed.
    :param int book_id:  The unique identifier of the book stored in DB.
    """
    logger.info("Started compressing book with name: {}".format(filename))

    compress_pdf(filename)

    logger.info("Book with id: '{}' compressed successfully!".format(book_id))


# ----------------------------------------------------------------------------------------------------------------------
@shared_task
def email_dispatch(heading, text):
    """
    Dispatches new project post data to multiple subscribed users.
    """
    recipients = TheUser.objects.filter(subscription=True)

    logger.info('Found {} subscribed users. Starting sending emails...'.format(len(recipients)))

    count_processed = 0
    for recipient in recipients:
        try:
            unsubscribe_token = '{}-{}'.format(recipient.id_user.username,
                                               int(time.mktime(recipient.id_user.date_joined.timetuple())))

            html_content = render_to_string('mails/email_dispatch.html', {'text': text, 'token': unsubscribe_token})
            text_content = strip_tags(html_content)
            subject = '{} - plamber.com.ua'.format(heading)

            email = EmailMultiAlternatives(subject, text_content, to=[recipient.id_user.email])
            email.attach_alternative(html_content, 'text/html')
            email.send()

            count_processed += 1
            if count_processed >= 400:
                logger.info('Sent "{}" emails. Stop sending for 24 hours..."'.format(count_processed))
                time.sleep(DAY_IN_SECONDS)

            logger.info('Successful processed "{}", sent to: "{}"'.format(count_processed, recipient.id_user.username))
            time.sleep(10)

        except NoReverseMatch:
            logger.info('Unexpected username: "{}"'.format(recipient.id_user.username))

    logger.info('Email dispatching has been finished.')
