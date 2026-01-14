import json
from typing import Optional

from europa.framework.queues.providers.api import BaseQueue, QueueItem


class RabbitMQQueue(BaseQueue):
    def __init__(self, channel, queue_name):
        self.channel = channel
        self.queue_name = queue_name
        self.channel.queue_declare(queue=self.queue_name)

    def enqueue(self, item: QueueItem) -> str:
        self.channel.basic_publish(exchange='',
                                   routing_key=self.queue_name,
                                   body=json.dumps(item.to_dict()))
        return item.id

    def dequeue(self) -> Optional[QueueItem]:
        method_frame, _, body = self.channel.basic_get(self.queue_name)
        if method_frame:
            self.channel.basic_ack(method_frame.delivery_tag)
            return QueueItem.from_dict(json.loads(body))
        return None

    def peek(self) -> Optional[QueueItem]:
        method_frame, _, body = self.channel.basic_get(self.queue_name, auto_ack=False)
        if method_frame:
            self.channel.basic_reject(method_frame.delivery_tag, requeue=True)
            return QueueItem.from_dict(json.loads(body))
        return None

    def size(self) -> int:
        queue_info = self.channel.queue_declare(queue=self.queue_name, passive=True)
        return queue_info.method.message_count

    def clear(self) -> None:
        self.channel.queue_purge(self.queue_name)