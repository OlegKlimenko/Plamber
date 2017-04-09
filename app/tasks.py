# -*- coding: utf-8 -*-

from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


# ----------------------------------------------------------------------------------------------------------------------
@shared_task
def send_mail(username, temp_password, recipient):
    """
    Celery task for sending mail on restore user data.

    :param str username:       The restored username.
    :param str temp_password:  The temporary password for restored username.
    :param str recipient:      The mail of recipient.
    """
    html_content = render_to_string('email.html', {'username': username, 'password': temp_password})
    text_content = strip_tags(html_content)
    subject = 'Восстановление аккаунта'

    email = EmailMultiAlternatives(subject, text_content, to=[recipient])
    email.attach_alternative(html_content, 'text/html')
    email.send()
