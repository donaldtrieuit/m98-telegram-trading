import json
import logging
import traceback
from typing import Callable, List, Optional

import pika
from pika.adapters import BlockingConnection
from pika.adapters.select_connection import SelectConnection

from common.utils.queue.i_broker import IBroker

logger = logging.getLogger(__name__)


class RabbitMqBroker(IBroker):
    def __init__(self, url):
        self.url = url
        self.channel = None
        self.queue_callbacks = {}
        self.create_exchange_request = []
        self.create_queue_request = []
        self.connection = self._blocking_connection()

    def create_topic(self, topic_name):
        if self.channel and self.channel.is_open:
            self.channel.exchange_declare(
                exchange=topic_name, exchange_type='topic', durable=True
            )
        else:
            self.create_exchange_request.append((topic_name, 'topic'))

    def create_broadcast_topic(self, topic_name):
        if self.channel and self.channel.is_open:
            self.channel.exchange_declare(
                exchange=topic_name, exchange_type='fanout', durable=True
            )
        else:
            self.create_exchange_request.append((topic_name, 'fanout'))

    def create_queue(self, queue, exchanges: List[str] = None, routing_keys: List[str] = None, auto_delete: bool = False):
        if self.channel and self.channel.is_open:
            self.channel.queue_declare(
                queue=queue, durable=True, auto_delete=auto_delete
            )
            for idx, exchange in enumerate(exchanges):
                self.channel.queue_bind(queue, exchange, routing_keys[idx])
        else:
            self.create_queue_request.append({
                'queue': queue,
                'exchanges': exchanges,
                'routing_keys': routing_keys,
                'auto_delete': auto_delete
            })

    def consume_queue(self, queue: str, message_callback: Callable, auto_ack: bool = True):
        self.queue_callbacks[queue] = (message_callback, auto_ack)
        if self.channel and self.channel.is_open:
            self._start_consume_queue(queue, message_callback, auto_ack)

    def start_consuming(self):
        self.channel.start_consuming()

    def publish_message(self, topic: str, routing_key: str, message: bytes):
        self.channel.basic_publish(topic, routing_key, message)

    def _selection_connection(self) -> SelectConnection:
        params = pika.URLParameters(self.url)
        parameters = pika.ConnectionParameters(
            host=params.host, port=params.port, credentials=params.credentials,
            connection_attempts=1000, retry_delay=10
        )
        self.connection = SelectConnection(
            parameters,
            on_open_callback=self._on_open_callback,
            on_close_callback=self._on_close_callback,
            on_open_error_callback=self._on_open_error_callback
        )
        logger.info(f'connection: {self.url} {self.connection}')
        return self.connection

    def _blocking_connection(self) -> Optional[BlockingConnection]:
        try:
            params = pika.URLParameters(self.url)
            parameters = pika.ConnectionParameters(
                host=params.host, port=params.port, credentials=params.credentials,
                connection_attempts=1000, retry_delay=10
            )
            self.connection = BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self._on_channel_open(self.channel)
            return self.connection
        except Exception as error:
            logger.error(error)
            traceback.print_exc()
            return None

    def _on_open_callback(self, _connection):
        self.channel = self.connection.channel()

    def _on_open_error_callback(self, _connection, error):
        logger.error(error)
        traceback.print_exc()

    def _on_close_callback(self, _connection, reason):
        logger.warning('Rabbitmq close connection')
        logger.info(reason)
        self._blocking_connection()

    def _on_channel_open(self, _channel):
        if len(self.create_exchange_request) > 0:
            for request in self.create_exchange_request:
                self.create_topic(request[0]) if request[1] == 'topic' else self.create_broadcast_topic(request[0])
            self.create_exchange_request = []

        if len(self.create_queue_request) > 0:
            for request in self.create_queue_request:
                self.create_queue(**request)

        for queue in self.queue_callbacks:
            (callback, auto_ack) = self.queue_callbacks[queue]
            self._start_consume_queue(queue, callback, auto_ack)

    def _start_consume_queue(self, queue, message_callback, auto_ack: bool = True):
        print("------Consume queue------")
        print(queue)

        def _on_message_callback(channel, method, properties, body):
            message = json.loads(body)
            message_callback(message)

        self.channel.basic_consume(queue, on_message_callback=_on_message_callback, auto_ack=auto_ack)

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        if self.connection is not None:
            logger.info('Closing connection')
            self.connection.close()
