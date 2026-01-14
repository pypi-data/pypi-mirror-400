# aiops_sdk/exceptions.py

import sys
import traceback
from .client import send_sync
from .payload import base_payload

def _excepthook(exc_type, exc, tb):
    payload = base_payload()
    payload.update({
        "signal_type": "exception",
        "status_code": 500,
        "error_type": exc_type.__name__,
        "message": str(exc),
        "stack_trace": "".join(
            traceback.format_exception(exc_type, exc, tb)
        ),
        "source": "process"
    })
    send_sync("/v1/sdk/exception", payload)

def register_exception_hook():
    sys.excepthook = _excepthook

def capture_exception(exc):
    payload = base_payload()
    payload.update({
        "signal_type": "exception",
        "status_code": 500,
        "error_type": type(exc).__name__,
        "message": str(exc),
        "stack_trace": traceback.format_exc(),
        "source": "manual"
    })
    send_sync("/v1/sdk/exception", payload)
