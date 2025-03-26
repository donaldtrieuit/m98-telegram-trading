import json

from django.conf import settings

from common.utils.queue.i_broker import IBroker


class TelegramSignalPublisher:
    def __init__(self, broker: IBroker):
        self.broker = broker
        self.broker.create_queue(
            settings.TELEGRAM_SUBSCRIPTION_QUEUE, [], ["#"], False
        )

    def publish(self, bot_id: int, channel_id: str, action: str):
        message = {
            "bot_id": bot_id,
            "channel_id": channel_id,
            "action": action,
        }
        b = json.dumps(message).encode('utf-8')
        self.broker.publish_message("", settings.TELEGRAM_SUBSCRIPTION_QUEUE, b)
