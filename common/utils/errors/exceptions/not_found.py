from django.utils.translation import gettext_lazy as _

from rest_framework import status

from common.utils.errors.exceptions.base import BaseError


class NotFoundError(BaseError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('No objects found.')
    default_code = 'not_found'
