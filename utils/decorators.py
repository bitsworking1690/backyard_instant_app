# -*- coding: utf-8 -*-
from functools import wraps
from django.http import JsonResponse
from rest_framework import status
from utils.util import response_data_formating


def require_json_content_type(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.content_type == "application/json":
            return view_func(request, *args, **kwargs)
        else:
            return JsonResponse(
                response_data_formating(
                    generalMessage="error",
                    data=None,
                    lang=None,
                    error=["Unsupported Media Type"],
                ),
                status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            )

    return _wrapped_view
