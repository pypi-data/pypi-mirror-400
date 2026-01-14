import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from europa.framework.service import (
    _BaseService,
    CalculationService,
    SingleQueueService,
)
from europa.framework.queues.queue_manager import QueueManager, QueueItem, QueueType


# Dummy CalculationService for testing
class DummyCalculationService(CalculationService):
    def __init__(self):
        super().__init__()
        self.called = False

    def calculate(self):
        self.called = True


# Dummy QueueManager and QueueItem for testing
class DummyQueueManager(QueueManager):
    def __init__(self):
        super().__init__(queue_type=QueueType.MEMORY)
    def dequeue(self):
        return QueueItem(payload={})


class DummySingleQueueService(SingleQueueService):
    def __init__(self):
        super().__init__()
        self.called = False
        self.queue_manager = DummyQueueManager()

    def calculate(self, queue_item):
        self.called = True


def test_get_status_endpoint():
    service = DummyCalculationService()
    client = TestClient(service.app)
    response = client.get("/get_status")
    assert response.status_code == 200
    assert response.json() == {"status": "running"}


def test_post_data_endpoint():
    service = DummyCalculationService()
    client = TestClient(service.app)
    response = client.post("/post_data", json={"foo": "bar"})
    assert response.status_code == 200
    assert response.json() == {"received": {"foo": "bar"}}


def test_calculation_loop_runs():
    service = DummyCalculationService()
    service.SLEEP_INTERVAL = 0.01
    # Patch _running to stop after one loop
    orig_calculate = service.calculate

    def stop_after_one():
        orig_calculate()
        service._running = False

    service.calculate = stop_after_one
    service._start()
    service._loop_thread.join(timeout=1)
    assert service.called


def test_queue_service_calculation_loop():
    service = DummySingleQueueService()
    service.SLEEP_INTERVAL = 0.01
    orig_calculate = service.calculate

    def stop_after_one(item):
        orig_calculate(item)
        service._running = False

    service.calculate = stop_after_one
    service._start()
    service._loop_thread.join(timeout=1)
    assert service.called


def test_custom_startup_called():
    class CustomService(DummyCalculationService):
        def __init__(self):
            super().__init__()
            self.startup_called = False

        def custom_startup(self):
            self.startup_called = True

    service = CustomService()
    service.SLEEP_INTERVAL = 0.01
    service._start()
    service._running = False
    assert service.startup_called


def test_abstract_methods_enforced():
    with pytest.raises(TypeError):
        _BaseService()
    with pytest.raises(TypeError):
        CalculationService()
    with pytest.raises(TypeError):
        SingleQueueService()


def test_exception_handling_in_calculation_loop():
    class ExceptionService(_BaseService):
        def _calculate(self):
            raise ValueError("Test exception!")

    service = ExceptionService()
    service.SLEEP_INTERVAL = 0.01
    service._running = True
    service.log = MagicMock()

    # Stop after one loop
    def stop_after_one():
        service._running = False

    service._pre_calculate = stop_after_one

    service._run_calculation_loop()

    # Check that error and traceback were logged
    error_calls = [
        call
        for call in service.log.error.call_args_list
        if "Unhandled exception" in str(call)
    ]
    traceback_calls = [
        call for call in service.log.error.call_args_list if "Traceback" in str(call)
    ]
    assert error_calls, "Error message not logged"
    assert traceback_calls, "Traceback not logged"
