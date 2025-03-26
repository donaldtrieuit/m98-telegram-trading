from django.utils.translation import gettext_lazy as _

from rest_framework import status

from common.utils.errors.exceptions.base import BaseError


class DuplicateBotError(BaseError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("The bot duplicated.")
    default_code = 'invalid'
