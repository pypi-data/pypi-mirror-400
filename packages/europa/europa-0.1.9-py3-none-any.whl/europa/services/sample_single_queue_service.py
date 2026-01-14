import time
import random
import os

from europa.framework.queues.queue_manager import QueueManager, QueueType, QueueItem
from europa.framework.service import SingleQueueService
from europa.framework.endpoint import expose


class SampleSinglePostgresQueueService(SingleQueueService):

    def custom_startup(self):
        self.queue_manager = QueueManager(
            queue_type=QueueType.POSTGRES,
            conn_params={
                "host": "localhost",
                "port": os.environ.get("DB_PORT"),
                "user": os.environ.get("DB_USER"),
                "password": os.environ.get("DB_PASSWORD"),
            },
            table_name="test_q_name",
        )
        item_id = self.queue_manager.enqueue({"count": 0})
        self.log.info(f"queued starting item with id: {item_id}")

    def calculate(self, queue_item: QueueItem):
        # Custom calculation logic for this service

        self.log.info(f"count = {queue_item.payload['count']}")
        payload = queue_item.payload
        payload["count"] += 1
        self.queue_manager.enqueue(payload)

        time.sleep(random.random())
        return None

    @expose.GET
    def example_endpoint(self):
        return {"message": "Hello World"}


class SampleSingleQueueService(SingleQueueService):

    def custom_startup(self):
        self.queue_manager = QueueManager(QueueType.MEMORY)
        self.queue_manager.enqueue({"count": 0})

    def calculate(self, queue_item: QueueItem):
        # Custom calculation logic for this service

        self.log.info(f"count = {queue_item.payload['count']}")
        payload = queue_item.payload
        payload["count"] += 1
        self.queue_manager.enqueue(payload)

        time.sleep(random.random())
        return None

    @expose.GET
    def example_endpoint(self):
        return {"message": "Hello World"}
