import json
from typing import Optional, List

from europa.framework.queues.providers.api import BaseQueue, QueueItem

class InMemoryQueue(BaseQueue):
    def __init__(self):
        self.queue: List[QueueItem] = []

    def enqueue(self, item: QueueItem) -> str:
        self.queue.append(item)
        return item.id

    def dequeue(self) -> Optional[QueueItem]:
        return self.queue.pop(0) if self.queue else None

    def peek(self) -> Optional[QueueItem]:
        return self.queue[0] if self.queue else None

    def size(self) -> int:
        return len(self.queue)

    def clear(self) -> None:
        self.queue.clear()
