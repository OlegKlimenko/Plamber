# -*- coding: utf-8 -*-
import json

from django.http import HttpResponse
from django.shortcuts import render

from ..forms import SendMessageForm
from ..models import Post, SupportMessage, Book


# ----------------------------------------------------------------------------------------------------------------------
def about(request):
    """
    Returns the about project main page.
    """
    if request.method == 'GET':
        return render(request, 'about.html', {'posts': Post.objects.all().order_by('-id'),
                                              'books_count': Book.objects.all().count()})

    else:
        return HttpResponse(status=404)


# ----------------------------------------------------------------------------------------------------------------------
def send_message(request):
    """
    Sends the message to system (moderators of resource).
    """
    if request.is_ajax():
        send_message_form = SendMessageForm(request.POST)

        if send_message_form.is_valid():
            SupportMessage.objects.create(email=send_message_form.cleaned_data['email'],
                                          text=send_message_form.cleaned_data['text'])

            return HttpResponse(json.dumps(True), content_type='application/json')
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=404)
