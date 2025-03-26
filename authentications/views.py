import logging
import uuid

from django.contrib.auth import logout
from django.shortcuts import redirect

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import \
    TokenObtainPairView as SimpleTokenObtainPairView

from authentications.serializers import (
    RefreshTokenSerializer,
    TokenObtainPairSerializer,
)

logger = logging.getLogger("authentications.view")


def generate_filename(filename):
    ext = filename.split('.')[-1]
    return '{}.{}'.format(uuid.uuid1(), ext)


class LogoutView(generics.GenericAPIView):
    serializer_class = RefreshTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            data = {
                "message": "Success"
            }
            return Response(data, status=status.HTTP_200_OK)


class TokenObtainPairView(SimpleTokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


def admin_logout_view(request):
    logout(request)
    return redirect("/admin/")
