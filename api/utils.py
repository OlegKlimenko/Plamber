# -*- coding: utf-8 -*-

from rest_framework import status
from rest_framework.response import Response


# ----------------------------------------------------------------------------------------------------------------------
def invalid_data_response(request_serializer):
    """
    Returns the error message depending on missing/invalid data in serializer.
    """
    return Response({'detail': request_serializer.errors,
                     'data': {}}, status=status.HTTP_400_BAD_REQUEST)
