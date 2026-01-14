from abc import ABC, abstractmethod
import sys
import signal
import atexit
import time
import traceback
from threading import Thread

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from europa.framework.logger import Logger
from europa.framework.endpoint import expose
from europa.framework.queues.queue_manager import (
    QueueFactory,
    QueueManager,
    QueueItem,
    QueueType,
)


class _BaseService(ABC):
    """
    Base class for microservices with a calculation loop and REST endpoints.
    """

    SLEEP_INTERVAL = 5.0

    def __init__(self):

        self.log = self._get_logger()

        self._running = False
        self._loop_thread = None

        self._register_signal_handlers()

        self.app = self._create_fastapi_app()
        self.router = self._register_exposed_methods(
            self.app
        )  # Register methods decorated with @expose.<METHOD>

    def _get_logger(self):
        """Initialize and return a logger instance."""
        return Logger(__name__)

    def _create_fastapi_app(self):
        """Create and configure the FastAPI app."""
        app = FastAPI(title=self.__class__.__name__)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # List of allowed origins
            allow_credentials=True,  # Allow cookies
            allow_methods=["*"],  # Allow all methods
            allow_headers=["*"],  # Allow all headers
        )
        app.add_event_handler("shutdown", self._on_shutdown)
        return app

    def _register_exposed_methods(self, app: FastAPI):
        """
        Scan for methods decorated with @expose.<METHOD> in the class and register
        them as REST endpoints in FastAPI's router
        """

        router = APIRouter()

        for attr_name in dir(self):  # Inspect the class, not the instance
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, "_http_method"):
                path = f"/{attr_name}"  # Derive path from method name (e.g., "get_status" -> "/get_status")
                method = getattr(
                    attr, "_http_method"  # Retrieve HTTP method from metadata
                )
                self.log.info(f"Registering route: {method} {path}")
                router.add_api_route(path, attr, methods=[method])

        app.include_router(router)  # Attach the router to the app

        return router

    def _register_signal_handlers(self):
        """Register signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self._handle_exit_signals)
        signal.signal(signal.SIGTERM, self._handle_exit_signals)

    def _start(self):
        """
        Start the calculation loop in a separate thread.
        """
        self._running = True

        # run custom startup before the calc loop starts
        self.custom_startup()

        self._loop_thread = Thread(target=self._run_calculation_loop, daemon=True)
        if not self._loop_thread.is_alive():
            self._loop_thread.start()

    def _handle_exit_signals(self, signum, frame):
        """Handle Ctrl+C and Kubernetes TERM signals"""
        self.log.info(f"Received signal {signum}, shutting down")
        self._on_shutdown()
        sys.exit(0)

    def _on_shutdown(self):
        """Cleanup during FastAPI shutdown"""
        self.log.info("FastAPI shutdown initiated")
        self.stop()
        if hasattr(self, "hazelcast_client") and self.hazelcast_client:
            self.hazelcast_client.shutdown()

    def stop(self):
        """Stop the calculation loop and wait for thread to finish"""
        self._running = False
        if self._loop_thread and self._loop_thread.is_alive():
            self._loop_thread.join(timeout=5)  # Wait up to 5 seconds
            if self._loop_thread.is_alive():
                self.log.warning("Thread did not terminate gracefully")

    def launch(self, port: int, enable_rest: bool = True):
        """
        Launch the FastAPI app using Uvicorn.
        Automatically starts the calculation loop before launching.
        """
        import uvicorn

        self._start()  # Start calculation loop in a seperate thread

        if enable_rest:
            uvicorn.run(self.app, host="0.0.0.0", port=port, log_level="debug")

    def _run_calculation_loop(self):
        """
        Continuous calculation loop running synchronously.
        Calls the `calculate()` method and sleeps for the specified interval.
        """
        while self._running:
            try:
                self._pre_calculate()
                self._calculate()
                self._post_calculate()
            except Exception as e:
                self.log.error(
                    f"❌ Unhandled exception in {self.__class__.__name__} calculation loop: {e}"
                )
                tb_str = traceback.format_exc()
                self.log.error(f"Traceback (most recent call last):\n{tb_str}")
            time.sleep(self.SLEEP_INTERVAL)  # Sleep for the configured interval

    def _pre_calculate(self):
        """ """
        pass

    @abstractmethod
    def _calculate(self):
        """
        This method needs to be implemented by the different TYPES of services
        classes (eg CalculationService, QueueService, etc)
        """

    def _post_calculate(self):
        """ """
        pass

    def custom_startup(self):
        """
        This function can be overriden to have a custom logic
        """
        pass

    @expose.GET
    def get_status(self):
        return {"status": "running"}

    @expose.POST
    def post_data(self, data: dict):
        return {"received": data}


class CalculationService(_BaseService):
    """
    Most basic type of Europa service, runs a single calculation loop
    """

    def __init__(self):
        super().__init__()

    def _calculate(self):
        """ """
        start_time = time.time()
        self.calculate()
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.log.info(f"Function 'calculate' executed in {elapsed_time:.4f} seconds")

    @abstractmethod
    def calculate(self):
        """
        This method needs to be implemented by the type of Calculation Service
        """


class SingleQueueService(_BaseService):
    """
    A single queue based Europa service. On each calculation loop, it picks a work item off
    the queue. The Queue provider is abstracted away so can be modified under the hood.
    """

    def __init__(self):
        super().__init__()

        self.queue_manager: QueueManager = None

    def _calculate(self):
        """Take a work item off the queue and give it to the calculate() method"""
        start_time = time.time()

        if self.queue_manager is None:
            raise RuntimeError(
                "queue_manager is not initialised on this service. Needs to be set in the custom startup logic."
            )

        queue_item = self.queue_manager.dequeue()
        self.calculate(queue_item)

        end_time = time.time()
        elapsed_time = end_time - start_time
        self.log.info(f"Function 'calculate' executed in {elapsed_time:.4f} seconds")

    @abstractmethod
    def calculate(self, queue_item: QueueItem):
        """
        This method needs to be implemented by the type of service
        """
