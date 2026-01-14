from websocket import create_connection, WebSocketApp
import threading
import time
from europa.framework.logger import Logger


class ThreadedWebSocketClient:
    def __init__(
        self,
        websocket_url,
        message_handler=None,
        opening_message=None,
        logger=None,
        keep_alive=False,
        ping_interval=30,
    ):
        """
        Initialize the WebSocket client.

        :param websocket_url: The WebSocket server URL to connect to.
        :param message_handler: A callback function to handle incoming messages.
        :param opening_message: A message to send upon connection.
        :param logger: An optional logger instance.
        :param keep_alive: Whether to enable WebSocket keep-alive (ping).
        :param ping_interval: Interval (in seconds) between pings.
        """
        self.websocket_url = websocket_url
        self.message_handler = message_handler
        self.opening_message = opening_message
        self.keep_alive = keep_alive
        self.ping_interval = ping_interval
        self.thread = None
        self.ping_thread = None
        self._running = False
        self.ws = None  # Store the WebSocket connection
        self.log = logger or Logger(
            __name__
        )  # Use the provided logger or create a default one

    def start(self):
        """
        Start the WebSocket client in a separate thread.
        """
        self._running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        self.log.debug("WebSocket client started.")

    def stop(self):
        """
        Stop the WebSocket client.
        """
        self._running = False
        if self.thread:
            self.thread.join()
        if self.ws:
            self.ws.close()
        self.log.info("WebSocket client stopped.")

    def _run(self):
        """
        Connect to the WebSocket server and listen for messages.
        """
        while self._running:
            try:
                # Define the on_open callback to send the opening message
                def on_open(ws):
                    if self.opening_message:
                        self.log.debug(
                            f"Sending opening message: {self.opening_message}"
                        )
                        ws.send(self.opening_message)

                # Use WebSocketApp to handle pings, pongs, and the opening message
                self.ws = WebSocketApp(
                    self.websocket_url,
                    on_open=on_open,
                    on_message=self._handle_message,
                    on_pong=self._handle_pong,
                    on_error=self._handle_error,
                )
                self.log.debug(f"Connecting to WebSocket: {self.websocket_url}")
                self.ws.run_forever(ping_interval=self.ping_interval)
            except Exception as e:
                self.log.error(f"WebSocket error: {e}")
            finally:
                # Ensure the WebSocket instance is cleaned up
                if self.ws:
                    self.ws.close()
                    self.ws = None
                if self._running:
                    time.sleep(5)  # Reconnect after a delay

    def _handle_message(self, ws, message):
        """
        Handle incoming WebSocket messages.

        :param ws: The WebSocket instance.
        :param message: The received WebSocket message.
        """
        if self.message_handler:
            self.message_handler(message)
        else:
            self.log.debug(f"Received WebSocket message: {message}")

    def _handle_pong(self, ws, message):
        """
        Handle pong responses from the WebSocket server.

        :param ws: The WebSocket instance.
        :param message: The pong message (can be empty).
        """
        self.log.debug("Received pong from WebSocket server.")

    def _handle_error(self, ws, error):
        """
        Handle WebSocket errors.

        :param ws: The WebSocket instance.
        :param error: The error message.
        """
        self.log.error(f"WebSocket error: {error}")

    def send_message(self, message):
        """
        Send a message through the WebSocket connection.

        :param message: The message to send.
        """
        if self.ws:
            try:
                self.ws.send(message)
                self.log.debug(f"Sent message: {message}")
            except Exception as e:
                self.log.error(f"Failed to send message: {e}")
        else:
            self.log.warning("WebSocket connection is not established.")
