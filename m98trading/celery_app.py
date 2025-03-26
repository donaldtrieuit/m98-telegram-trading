"""The Celery application."""

import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings  # noqa
from celery.signals import setup_logging


os.environ['DJANGO_SETTINGS_MODULE'] = 'm98trading.settings'

app = Celery('m98trading')

app.config_from_object('m98trading.settings', namespace='CELERY')

app.conf.task_default_priority = 1
app.conf.timezone = 'UTC'
app.conf.beat_schedule = {
    'sync_bot_tasks': {
        'task': 'trade_bot.tasks.sync_tasks_status',
        'schedule': crontab(minute='*/10'),  # Run each 10 mins
    },
}


@setup_logging.connect
def config_loggers(*args, **kwags):
    from logging.config import dictConfig
    from django.conf import settings
    dictConfig(settings.LOGGING)


app.autodiscover_tasks()
