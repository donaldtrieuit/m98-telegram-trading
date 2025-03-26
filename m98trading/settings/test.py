ENV_NAME = "Test"
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = 'django-db'
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}
EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"
CSRF_TRUSTED_ORIGINS = ["http://localhost:8000"]
