

from europa.framework.sockets import ThreadedWebSocketClient
from europa.framework.service import CalculationService
from europa.framework.endpoint import expose

class SampleServiceWithWebsocket(CalculationService):

    message = None
    count = 0

    def custom_startup(self):
        self.websocket_client = ThreadedWebSocketClient(
            websocket_url="wss://echo.websocket.org",
            message_handler=self.process_websocket_message,
            opening_message="Hi im an opening message",
            logger=self.log,
            keep_alive=True,
            ping_interval=5
        )
        self.websocket_client.start()

    def calculate(self):
        self.count += 1
        self.websocket_client.send_message(f"New count = {self.count}")


    @expose.GET
    async def send_message(self, message: str):
        self.websocket_client.send_message(message)

    def process_websocket_message(self, message):
        """
        Process incoming WebSocket messages.
        """
        print(f"Processing WebSocket message: {message}")
        self.message = message

