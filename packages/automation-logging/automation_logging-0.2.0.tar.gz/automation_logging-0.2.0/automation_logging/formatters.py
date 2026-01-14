import json
import logging
import platform
import getpass
import os


class DefaultFormatter(logging.Formatter):
    """Standard human-readable formatter"""

    def __init__(self, datefmt: str = "%Y-%m-%d %H:%M:%S%z"):
        system_name = platform.node()
        user = f"{os.environ.get('USERDOMAIN', '-')}\\{getpass.getuser()}"
        log_format = (
            f"%(asctime)s | {system_name} | {user} | %(name)s"
            " | %(levelname)s | %(frame_info)s | %(message)s"
        )
        super().__init__(fmt=log_format, datefmt=datefmt)


class JsonFormatter(logging.Formatter):
    """
    Custom JSON formatter for logging.
    Flattens dictionary messages (STAT) into the root JSON object.
    """

    def __init__(self, datefmt: str = "%Y-%m-%d %H:%M:%S%z"):
        super().__init__(datefmt=datefmt)
        self.system_name = platform.node()
        self.user = f"{os.environ.get('USERDOMAIN', '-')}\\{getpass.getuser()}"

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "system": self.system_name,
            "user": self.user,
            "frame_info": getattr(record, "frame_info", "unknown"),
        }

        if isinstance(record.msg, dict):
            log_entry.update(record.msg)
            log_entry["message"] = "structured_data"
        else:
            log_entry["message"] = record.getMessage()

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False)
