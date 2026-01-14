import time
import random

from europa.framework.service import CalculationService
from europa.framework.endpoint import expose


class SampleService(CalculationService):

    count = 0

    def calculate(self):
        # Custom calculation logic for this service
        self.count += 1
        print(f"count = {self.count}")
        time.sleep(random.random())
        return None

    @expose.GET
    async def example_endpoint(self):
        return {"message": "Hello World"}
