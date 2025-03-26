import logging

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import \
    TokenObtainPairSerializer as SimpleTokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger("accounts.serializer")


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': _('Token is invalid or expired')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')


class TokenObtainPairSerializer(SimpleTokenObtainPairSerializer):
    default_error_messages = {
        'no_active_account': _('No active account found with the given credentials')
    }
