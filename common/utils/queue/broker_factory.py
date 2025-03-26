from django.conf import settings

from common.utils.queue.i_broker import IBroker
from common.utils.queue.rabbitmq_broker import RabbitMqBroker
from common.utils.queue.test_broker import TestBroker


class BrokerFactory:
    @staticmethod
    def get_broker() -> IBroker:
        if settings.BROKER_TYPE == "rabbitmq":
            return RabbitMqBroker(settings.CELERY_BROKER_URL)
        else:
            return TestBroker()
