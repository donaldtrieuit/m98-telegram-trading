import logging
import os

from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Bots

logger = logging.getLogger(__name__)


@receiver(post_delete, sender=Bots, dispatch_uid="after_destroy_bot")
def handle_destroy_bot(sender, instance, **kwargs):
    for i in range(int(settings.LOGGING_BACKUP_COUNT)):
        log_file = settings.MEDIA_ROOT + '/{}_bot_log.log'.format(instance.id)
        if i != 0:
            log_file = settings.MEDIA_ROOT + '/{}_bot_log.log.{}'.format(instance.id, i)
        if os.path.exists(log_file):
            try:
                os.remove(log_file)
            except Exception as ex:
                logger.error(ex)
