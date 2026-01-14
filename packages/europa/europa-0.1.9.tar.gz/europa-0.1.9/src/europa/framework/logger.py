import logging


class Logger:
    """
    A wrapper class for logging to allow easy replacement with other logging mechanisms.
    """

    def __init__(self, name: str, level: int = logging.INFO):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s")
            )
            self._logger.addHandler(handler)
        # Allow logs to propagate to root logger so other libraries' logs print as normal
        self._logger.propagate = True

    def set_level(self, level):
        self._logger.setLevel(level)

    def debug(self, message: str):
        self._logger.debug(message)

    def info(self, message: str):
        self._logger.info(message)

    def warning(self, message: str):
        self._logger.warning(message)

    def error(self, message: str):
        self._logger.error(message)

    def critical(self, message: str):
        self._logger.critical(message)
