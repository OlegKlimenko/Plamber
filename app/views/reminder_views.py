# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from ..forms import UpdateReminderForm
from ..models import TheUser


# ----------------------------------------------------------------------------------------------------------------------
def update_reminder(request):
    """
    Changes the reminder status.
    """
    if request.method == 'POST' and request.user.is_authenticated():
        form = UpdateReminderForm(request.POST)

        if form.is_valid():
            the_user = get_object_or_404(TheUser, id_user=request.user)
            the_user.update_reminder(form.cleaned_data['field'], form.cleaned_data['value'])

            return HttpResponse(status=200)
        return HttpResponse(status=404)
    return HttpResponse(status=404)
