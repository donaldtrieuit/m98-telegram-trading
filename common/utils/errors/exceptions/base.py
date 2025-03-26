from django.utils.encoding import force_str
from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList


class BaseError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Could not process this request because of an internal error.')
    default_code = 'internal_error'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        self.detail = _get_error_details(detail, code)


def _get_error_details(data, default_code=None):
    if isinstance(data, (list, tuple)):
        ret = [
            _get_error_details(item, default_code) for item in data
        ]
        if isinstance(data, ReturnList):
            return ReturnList(ret, serializer=data.serializer)
        return ret
    elif isinstance(data, dict):
        ret = {
            key: _get_error_details(value, default_code)
            for key, value in data.items()
        }
        if isinstance(data, ReturnDict):
            return ReturnDict(ret, serializer=data.serializer)
        return ret

    text = force_str(data)
    ret = {
        "message": text
    }
    return ret
