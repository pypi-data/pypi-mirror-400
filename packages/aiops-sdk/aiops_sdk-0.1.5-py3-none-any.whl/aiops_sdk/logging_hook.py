import logging
import traceback
from .client import send_sync
from .payload import base_payload

class AIOpsLogHandler(logging.Handler):
    def emit(self, record):
        if record.levelno < logging.ERROR:
            return

        payload = base_payload()
        payload.update({
            "error_type": record.levelname,
            "message": record.getMessage(),
            "stack_trace": record.exc_text or "",
            "source": "logging"
        })

        send_sync("/v1/sdk/exception", payload)

def attach_logging_handler():
    root = logging.getLogger()
    root.addHandler(AIOpsLogHandler())
