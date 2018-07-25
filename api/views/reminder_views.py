# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..serializers.request_serializers import GetReminderRequest, UpdateReminderRequest
from ..utils import invalid_data_response, validate_api_secret_key
from app.models import TheUser


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def get_reminders(request):
    """
    Returns the reminders status.
    """
    validate_api_secret_key(request.data.get('app_key'))

    request_serializer = GetReminderRequest(data=request.data)

    if request_serializer.is_valid():
        the_user = get_object_or_404(TheUser, auth_token=request.data.get('user_token'))

        return Response({'detail': 'successful',
                         'data': the_user.get_api_reminders()},
                        status=status.HTTP_200_OK)
    else:
        return invalid_data_response(request_serializer)


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def update_reminder(request):
    """
    Changes the status of the reminder.
    """
    validate_api_secret_key(request.data.get('app_key'))

    request_serializer = UpdateReminderRequest(data=request.data)

    if request_serializer.is_valid():
        the_user = get_object_or_404(TheUser, auth_token=request.data.get('user_token'))
        the_user.update_reminder(request.data.get('field'), request.data.get('value'))

        return Response({'detail': 'successful'},
                        status=status.HTTP_200_OK)
    else:
        return invalid_data_response(request_serializer)
