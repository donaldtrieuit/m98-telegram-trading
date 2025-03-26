from typing import Callable, Dict, List

from common.utils.queue.i_broker import IBroker


class TestBroker(IBroker):
    def create_topic(self, topic_name):
        pass

    def create_broadcast_topic(self, topic_name):
        pass

    def create_queue(self, queue, exchanges: List[str] = None, routing_keys: List[str] = None,
                     auto_delete: bool = False):
        pass

    def consume_queue(self, queue: str, message_callback: Callable[[Dict], None], auto_ack: bool = True):
        pass

    def publish_message(self, topic: str, routing_key: str, message: bytes):
        pass
