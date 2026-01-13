import logging
from typing import Optional
from enum import Enum

class LogCategory(Enum):
    CONNECTION = "connection"
    PROTOCOL = "protocol"
    DATA_TRANSFER = "data_transfer"
    NOTIFICATION = "notification"
    COMMAND = "command"

class GiciskyLogger:
    def __init__(self, logger: Optional[logging.Logger] = None):
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger("gicisky")
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter('[%(name)s] %(levelname)s: %(message)s')
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
                self.logger.setLevel(logging.INFO)

    def log(self, level: int, message: str, category: LogCategory = None, **kwargs):
        extra_info = ""
        if category:
            extra_info = f"[{category.value}] "

        self.logger.log(level, f"{extra_info}{message}", **kwargs)

    def debug(self, message: str, category: LogCategory = None):
        self.log(logging.DEBUG, message, category)

    def info(self, message: str, category: LogCategory = None):
        self.log(logging.INFO, message, category)

    def warning(self, message: str, category: LogCategory = None):
        self.log(logging.WARNING, message, category)

    def error(self, message: str, category: LogCategory = None):
        self.log(logging.ERROR, message, category)
