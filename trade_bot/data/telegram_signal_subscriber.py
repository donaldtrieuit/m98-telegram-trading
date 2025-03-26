import logging
import threading
import traceback
import uuid
from typing import Callable, Dict

from django.conf import settings

from common.utils.queue.i_broker import IBroker
from trade_bot.dto.telegram_signal_dto import TradingSignal

logger = logging.getLogger(__name__)


class TelegramSignalSubscriber:
    def __init__(self, broker: IBroker):
        self.broker = broker
        self.queue_name = f'telegram_message_subscribe_{uuid.uuid4()}'
        broker.create_topic(settings.TELEGRAM_MESSAGE_TOPIC)
        broker.create_queue(
            self.queue_name, [settings.TELEGRAM_MESSAGE_TOPIC], ["#"], True
        )

    def subscribe(self, message_callback: Callable[[str, TradingSignal, str], None]):
        def callback(message: Dict):
            try:
                logger.info(f"Telegram signal: {message}")
                message_callback(message['channel_id'], TradingSignal(**message['signal']), message['date'])
            except Exception as e:
                print(e)
                traceback.print_exc()

        self.broker.consume_queue(self.queue_name, callback)

        threading.Thread(target=self.broker.start_consuming, args=()).start()
