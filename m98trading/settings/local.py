# SECURITY WARNING: don't run with debug turned on in production!
import environ

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
# reading .env file
environ.Env.read_env()

DEBUG = True
ALLOWED_HOSTS = ['*']
EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"
CSRF_TRUSTED_ORIGINS = ["http://localhost:8000"]
