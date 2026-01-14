import json
from typing import Any, Dict, Optional
from enum import StrEnum

from europa.framework.queues.providers.api import BaseQueue, QueueItem
from europa.framework.queues.providers import (
    PostgresQueue,
    InMemoryQueue,
    RabbitMQQueue,
    RedisQueue,
)


class QueueType(StrEnum):
    MEMORY = "MEMORY"
    POSTGRES = "POSTGRES"
    REDIS = "REDIS"
    RABBITMQ = "RABBITMQ"


class QueueFactory:
    @staticmethod
    def create_queue(queue_type: QueueType, **kwargs) -> BaseQueue:
        if queue_type == QueueType.MEMORY:
            return InMemoryQueue()
        elif queue_type == QueueType.POSTGRES:
            conn_params = kwargs.get("conn_params")
            table_name=kwargs.get("table_name")
            if conn_params is None or table_name is None:
                raise ValueError("Both conn_params and table_name must be set to use a postgres queue.")
                                     
            return PostgresQueue(
                conn_params=conn_params,
                table_name=table_name,
            )
        elif queue_type == QueueType.REDIS:
            import redis

            redis_client = redis.Redis(**kwargs)
            return RedisQueue(redis_client)
        elif queue_type == QueueType.RABBITMQ:
            import pika

            connection = pika.BlockingConnection(pika.ConnectionParameters(**kwargs))
            channel = connection.channel()
            return RabbitMQQueue(channel, kwargs.get("queue_name", "default_queue"))
        else:
            raise ValueError(f"Unsupported queue type: {queue_type}")


class QueueManager:
    def __init__(self, queue_type: str, **kwargs):
        self.queue = QueueFactory.create_queue(queue_type, **kwargs)

    def change_queue_provider(self, new_queue_type: QueueType, **kwargs):
        new_queue = QueueFactory.create_queue(new_queue_type, **kwargs)

        # Transfer items from old queue to new queue
        while True:
            item = self.queue.dequeue()
            if item is None:
                break
            new_queue.enqueue(item)

        self.queue = new_queue

    def enqueue(
        self, payload: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        item = QueueItem(payload, metadata)
        return self.queue.enqueue(item)

    def dequeue(self) -> Optional[QueueItem]:
        return self.queue.dequeue()

    def peek(self) -> Optional[QueueItem]:
        return self.queue.peek()

    def size(self) -> int:
        return self.queue.size()

    def clear(self) -> None:
        self.queue.clear()
