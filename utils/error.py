from rest_framework import status
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from enum import Enum
import logging

logger = logging.getLogger("django")


class Error(Enum):
    DEFAULT_ERROR = {"detail": _("{}")}


class APIError:
    def __init__(self, error: Error, extra=None):
        self.error = error
        self.extra = extra or None
        error_detail = error.value
        if self.extra:
            if isinstance(self.extra, list):
                error_detail["detail"] = {
                    "message": "error",
                    "error": self.extra,
                    "data": None,
                }
        try:
            logger.info(error.value)
        except BaseException as be:
            logger.error(be)
        raise ValidationError(**error_detail)
