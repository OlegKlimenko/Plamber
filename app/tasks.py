# -*- coding: utf-8 -*-

import logging
import time
import requests

from celery import shared_task
from django.conf import settings
from django.template.loader import render_to_string
from django.urls.exceptions import NoReverseMatch

from .utils import compress_pdf
from .models import TheUser

logger = logging.getLogger('changes')


# ----------------------------------------------------------------------------------------------------------------------
def send_message(recipient, subject, html_content):
    """
    Sends the post request to MAILGUN api to push email.

    :param str recipient:    Email of the recipient.
    :param str subject:      Email subject.
    :param str html_content: Email content in HTML format.
    :return:
    """
    return requests.post(
        settings.MAILGUN_DOMAIN,
        auth=('api', settings.MAILGUN_API_KEY),
        data={'from': settings.MAILGUN_FROM_MAIL,
              'to': [recipient],
              'subject': subject,
              'html': html_content}
    )

# ----------------------------------------------------------------------------------------------------------------------
@shared_task
def successful_registration(username, recipient):
    """
    Celery task for sending welcome mail after creating new user.

    :param str username:   The restored username.
    :param str recipient:  The mail recipient.
    """
    html_content = render_to_string('mails/registration_success.html', {'username': username})
    subject = 'Успешная регистрация - plamber.com.ua'

    resp = send_message(recipient, subject, html_content)
    logger.info("Sent successful registration message to '{}' with message '{}'".format(recipient, resp.text))


# ----------------------------------------------------------------------------------------------------------------------
@shared_task
def restore_account(username, temp_password, recipient):
    """
    Celery task for sending mail on restore user data.

    :param str username:       The restored username.
    :param str temp_password:  The temporary password for restored username.
    :param str recipient:      The mail recipient.
    """
    html_content = render_to_string(
        'mails/account_restore.html',
        {'username': username, 'password': temp_password, 'email_host_user': settings.EMAIL_HOST_USER}
    )
    subject = 'Восстановление аккаунта - plamber.com.ua'

    resp = send_message(recipient, subject, html_content)
    logger.info("Sent successful registration message to '{}' with message '{}'".format(recipient, resp.text))


# ----------------------------------------------------------------------------------------------------------------------
@shared_task
def changed_password(username, recipient):
    """
    Celery task for sending mail, to notify user about password changed.

    :param str username:   The restored username.
    :param str recipient:  The mail recipient.
    """
    html_content = render_to_string('mails/password_changed.html',
                                    {'username': username, 'email_host_user': settings.EMAIL_HOST_USER})
    subject = 'Изменение пароля аккаунта - plamber.com.ua'

    resp = send_message(recipient, subject, html_content)
    logger.info("Sent successful registration message to '{}' with message '{}'".format(recipient, resp.text))


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

    for number, recipient in enumerate(recipients):
        if recipient.id_user.email:
            try:
                unsubscribe_token = '{}-{}'.format(recipient.id_user.username,
                                                   int(time.mktime(recipient.id_user.date_joined.timetuple())))

                html_content = render_to_string(
                    'mails/email_dispatch.html',
                    {'text': text, 'token': unsubscribe_token, 'email_host_user': settings.EMAIL_HOST_USER}
                )
                subject = '{} - plamber.com.ua'.format(heading)

                resp = send_message(recipient.id_user.email, subject, html_content)

                logger.info('Successful processed "{}", sent to: "{}"'.format(number, recipient.id_user.username))
                logger.info('Mailgun response {}'.format(resp.text))

            except NoReverseMatch:
                logger.info('Unexpected username: "{}"'.format(recipient.id_user.username))

    logger.info('Email dispatching has been finished.')
