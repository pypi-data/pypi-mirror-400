import json
from typing import Optional

from europa.framework.queues.providers.api import BaseQueue, QueueItem

class RedisQueue(BaseQueue):
    def __init__(self, redis_client):
        self.redis = redis_client
        self.queue_key = "abstract_queue"

    def enqueue(self, item: QueueItem) -> str:
        self.redis.rpush(self.queue_key, json.dumps(item.to_dict()))
        return item.id

    def dequeue(self) -> Optional[QueueItem]:
        item_data = self.redis.lpop(self.queue_key)
        return QueueItem.from_dict(json.loads(item_data)) if item_data else None

    def peek(self) -> Optional[QueueItem]:
        item_data = self.redis.lindex(self.queue_key, 0)
        return QueueItem.from_dict(json.loads(item_data)) if item_data else None

    def size(self) -> int:
        return self.redis.llen(self.queue_key)

    def clear(self) -> None:
        self.redis.delete(self.queue_key)
