DEBUG = False
ALLOWED_HOSTS = ['*']
EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"
BASE_URL = "https://m98trading.io"
MANAGER_URL = "https://m98trading.io"
CSRF_TRUSTED_ORIGINS = ["https://m98trading.io"]
MAILGUN_SENDER_NAME = "M98 Automating Trading"
MAILGUN_SENDER_EMAIL = "supporter@m98trading.io"
