from abc import ABC, abstractmethod
import json
from typing import Any, Dict, Optional
import uuid
from datetime import datetime

class QueueItem:
    def __init__(self, payload: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now().isoformat()
        self.payload = payload
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "payload": self.payload,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueueItem':
        item = cls(payload=data["payload"], metadata=data["metadata"])
        item.id = data["id"]
        item.created_at = data["created_at"]
        return item

class BaseQueue(ABC):
    @abstractmethod
    def enqueue(self, item: QueueItem) -> str:
        pass

    @abstractmethod
    def dequeue(self) -> Optional[QueueItem]:
        pass

    @abstractmethod
    def peek(self) -> Optional[QueueItem]:
        pass

    @abstractmethod
    def size(self) -> int:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

