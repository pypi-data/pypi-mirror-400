import time
import random
import signal
import atexit
import os

from europa.framework.service import CalculationService
from europa.framework.endpoint import expose

import hazelcast


HZ_HOST = "localhost"
HZ_PORT = "5701"

class PythiaHazelcast:
    def __init__(self):

        if HZ_HOST is None or HZ_HOST == "":
            raise ValueError("HZ_HOST must be set in environment vars")

        if HZ_PORT is None or HZ_PORT == "":
            raise ValueError("HZ_PORT must be set in environment vars")

        self.client = hazelcast.HazelcastClient(
            cluster_name="pythia-hz-cluster",
            cluster_members=[f"{HZ_HOST}:{HZ_PORT}"],
        )
        # Register cleanup handlers
        signal.signal(signal.SIGTERM, self._shutdown)
        signal.signal(signal.SIGINT, self._shutdown)
        atexit.register(self._shutdown)

    def _shutdown(self, *args):
        if self.client:
            self.client.shutdown()


class SampleServiceWithHazelcast(CalculationService):

    count = 0

    def custom_startup(self):
        self.hz = PythiaHazelcast()
        self.hz.client.get_map("poz")

    def calculate(self):
        # Custom calculation logic for this service
        self.count += 1
        print(f"count = {self.count}")
        time.sleep(random.random())
        return None

    @expose.GET
    async def example_endpoint(self):
        return {"message": "Hello World"}
