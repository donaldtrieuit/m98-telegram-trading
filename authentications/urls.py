from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from authentications.views import LogoutView, TokenObtainPairView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    path('auth/logout/', csrf_exempt(LogoutView.as_view()), name="auth-logout"),
    path('auth/token/', csrf_exempt(TokenObtainPairView.as_view()), name='token_obtain_pair'),
    path('auth/token/refresh/', csrf_exempt(TokenRefreshView.as_view()), name='token_refresh'),
]
