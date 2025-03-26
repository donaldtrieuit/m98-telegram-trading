import logging
import time

from django.db.models import Q

from common.utils import remote_lock_util
from m98trading import settings
from m98trading.celery_app import app
from trade_bot.bots.running_bot_manager import (
    start_bot_runner,
    stop_running_bot,
)
from trade_bot.models import Bots

logger = logging.getLogger(__name__)


@app.task(bind=True)
def start_vol_bot(self, bot_id):
    bot = Bots.objects.get(pk=bot_id)
    bot.task_id = self.request.id
    bot.save()
    acquired_lock = remote_lock_util.acquire(f"bot_{bot.id}", 60 + 15)
    if not acquired_lock:
        logger.info(f"Bot: {bot.id} - task id: {bot.task_id} already running")
        return
    if bot.status != 'off':
        start_bot_runner(bot, self.request.id)


@app.task(max_retries=1)
def sync_tasks_status():
    """sync bot tasks"""
    acquired = remote_lock_util.acquire('sync_tasks_status', None)
    if not acquired:
        return
    logger.info('--------START sync_tasks_status ---------')
    try:
        bots = Bots.objects.filter(Q(status='on') | Q(status='pause')).all()
        logger.info(f'Found {len(bots)} bot tasks')
        for bot in bots:
            logger.info("Checking for bot: {} - task id: {}".format(bot.id, bot.task_id))
            is_running = remote_lock_util.get_key(f"bot_{bot.id}")
            if is_running == '1':
                logger.info(f"bot: {bot.id} - task id: {bot.task_id} already running")
                continue
            start_vol_bot.apply_async(args=[bot.id], queue=f"{settings.BOT_QUEUE_NAME}")
            # sleep to prevent multi bot running at same time slot
            time.sleep(2)
    except Exception as e:
        logger.error(e)
    finally:
        logger.info('--------END sync_tasks_status ---------')
        remote_lock_util.release('sync_tasks_status')


@app.task
def kill_task_running_bot(bot_id, task_id):
    logger.info(f"Terminating task {task_id} running bot [{bot_id}]")
    stop_running_bot(bot_id)
    remote_lock_util.release(f"bot_{bot_id}")
