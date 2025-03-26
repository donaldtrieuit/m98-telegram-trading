"""
URL configuration for m98trading project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView

from drf_yasg import generators, openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from authentications.views import admin_logout_view

admin.site.site_title = _('M98 Automation Trading')
admin.site.site_header = _('M98 Automation Trading')


class BothHttpAndHttpsSchemaGenerator(generators.OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ["http", "https"]
        return schema


public_patterns = []


schema_view = get_schema_view(
    openapi.Info(
        title="Django Template API",
        default_version='v1',
        description="M98 Automation Trading",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    generator_class=BothHttpAndHttpsSchemaGenerator,
    permission_classes=[permissions.AllowAny],
    patterns=[path("", include(public_patterns))],
)

urlpatterns = [
    # web route
    path('admin/logout/', admin_logout_view, name="logout"),
    path('admin/', admin.site.urls),

    re_path(r'^$', RedirectView.as_view(url='/admin')),

    # api route
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),

    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # health check
    re_path(r'^ht/m7jhMG9Yii65kNnhp8wVxKcU6AkgVx/$', include('health_check.urls')),
] + public_patterns

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
