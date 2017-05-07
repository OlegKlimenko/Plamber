# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render

from ..models import Post


# ----------------------------------------------------------------------------------------------------------------------
def about(request):
    """
    Returns the about project main page.

    :param django.core.handlers.wsgi.WSGIRequest request: The request for adding book.
    :return: The about project main page.
    """
    if request.method == 'GET':
        return render(request, 'about.html', {'posts': Post.objects.all().order_by('-id')})

    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def send_message(request):
    """
    Sends the message to system (moderators of resource).

    :param django.core.handlers.wsgi.WSGIRequest request: The request for sending message.
    :return: Response status
    """
#     if request.is_ajax():
#         send_message_form = SendMessageForm(request.POST)
#
#         try:
#             if send_message_form.is_valid():
#                 send_mail(
#                     'To technical support',
#                     send_message_form.cleaned_data['text'],
#                     send_message_form.cleaned_data['mailer'],
#                     ['oleg_klimenko@inbox.ru'],
#                     fail_silently=True
#                 )
#                 return HttpResponse(json.dumps(True), content_type='application/json')
#         except Exception as e:
#             import traceback
#             print(traceback.print_exc())
#     else:
#         return HttpResponse(status=404)
