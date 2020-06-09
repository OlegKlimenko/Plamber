# -*- coding: utf-8 -*-
import json

from django.http import HttpResponse
from django.shortcuts import render

from ..forms import SendMessageForm
from ..models import Post, SupportMessage, Book
from ..views import process_method, process_ajax, process_form


# ----------------------------------------------------------------------------------------------------------------------
@process_method('GET', 404)
def about(request):
    """
    Returns the about project main page.
    """
    return render(request, 'about.html', {'posts': Post.objects.all().order_by('-id'),
                                          'books_count': Book.objects.all().count()})


# ----------------------------------------------------------------------------------------------------------------------
@process_ajax(404)
@process_form('POST', SendMessageForm, 400)
def send_message(request, form):
    """
    Sends the message to system (moderators of resource).
    """
    SupportMessage.objects.create(email=form.cleaned_data['email'],
                                  text=form.cleaned_data['text'])

    return HttpResponse(json.dumps(True), content_type='application/json')
