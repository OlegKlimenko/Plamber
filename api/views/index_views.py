# -*- coding: utf-8 -*-

from django.contrib.auth import authenticate, login
from rest_framework.decorators import api_view
from rest_framework.response import Response

from app.models import TheUser


# ----------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def user_login(request):
    """
    Authenticates user and returns the token which uses to access to the API.
    """
    user = authenticate(username=request.data.get('username'),
                        password=request.data.get('password'))
    if user:
        user_token = TheUser.objects.get(id_user=user).auth_token

        login(request, user)
        return Response({'status': 200,
                         'detail': 'successful',
                         'data': {'token': user_token}})

    return Response({'status': 404,
                     'detail': 'not authenticated',
                     'data': {'token': None}})
