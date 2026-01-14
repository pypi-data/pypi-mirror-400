import logging
import sys

class Logger:
    """
    Simple wrapper around Python's logging module for AutoPX.
    """

    def __init__(self, name="AutoPX", level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Avoid multiple handlers
        if not self.logger.handlers:
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(level)
            formatter = logging.Formatter("[%(levelname)s] %(message)s")
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def info(self, msg: str):
        self.logger.info(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def debug(self, msg: str):
        self.logger.debug(msg)
