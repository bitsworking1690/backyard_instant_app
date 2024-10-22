from rest_framework import status
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException
from enum import Enum
import logging

logger = logging.getLogger("django")

class Error(Enum):
    DEFAULT_ERROR = {"detail": _("{}"), "status_code": status.HTTP_400_BAD_REQUEST}
    INVALID_JWT_TOKEN = {"detail": _("Invalid token!"), "status_code": status.HTTP_401_UNAUTHORIZED}


class CustomValidationError(APIException):
    def __init__(self, detail=None, status_code=status.HTTP_400_BAD_REQUEST):
        self.status_code = status_code
        self.detail = detail or _('Invalid input.')

        if not isinstance(self.detail, (dict, list)):
            self.detail = [self.detail]


class APIError:
    def __init__(self, error: Error, extra=None):
        self.error = error
        self.extra = extra or None
        error_detail = self._prepare_error_detail()

        try:
            logger.info(error_detail)
        except Exception as be:
            logger.error(f"Logging error: {be}")

        raise CustomValidationError(detail=error_detail['detail'], status_code=error_detail['status_code'])

    def _prepare_error_detail(self):
        detail = self.error.value["detail"]
        status_code = self.error.value.get("status_code", status.HTTP_400_BAD_REQUEST)

        if self.extra:
            detail = detail.format(self.extra)

        return {"detail": detail, "status_code": status_code}
