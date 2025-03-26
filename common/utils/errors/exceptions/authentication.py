from django.utils.translation import gettext_lazy as _

from rest_framework import status

from common.utils.errors.exceptions.base import BaseError


class ChangePasswordError(BaseError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Password unsuccessfully updated.')
    default_code = 'invalid'


class ChangeEmailError(BaseError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Email unsuccessfully updated.')
    default_code = 'invalid'


class ResetPasswordError(BaseError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Password unsuccessfully reset.')
    default_code = 'invalid'


class RegisterError(BaseError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('A user with username or email already exists.')
    default_code = 'invalid'


class AuthenticateError(BaseError):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('Unauthorized.')
    default_code = 'invalid'


class Forbidden(BaseError):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _("You don't have permission.")
    default_code = 'forbidden'
