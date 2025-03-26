from typing import Callable, Dict, List


class IBroker:
    def create_topic(self, topic_name):
        raise 'Method not implemented'

    def create_broadcast_topic(self, topic_name):
        raise 'Method not implemented'

    def create_queue(self, queue, exchanges: List[str] = None, routing_keys: List[str] = None,
                     auto_delete: bool = False):
        raise 'Method not implemented'

    def consume_queue(self, queue: str, message_callback: Callable[[Dict], None], auto_ack: bool = True):
        raise 'Method not implemented'

    def start_consuming(self):
        raise 'Method not implemented'

    def publish_message(self, topic: str, routing_key: str, message: bytes):
        raise 'Method not implemented'

    def close_connection(self):
        raise 'Method not implemented'
