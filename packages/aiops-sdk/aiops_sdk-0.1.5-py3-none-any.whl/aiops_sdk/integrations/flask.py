# aiops_sdk/integrations/flask.py

from flask import got_request_exception, request
from ..exceptions import capture_exception
from ..payload import base_payload
from ..client import send_sync


def init_flask(app):
    """
    Flask integration for AIOps SDK.

    Captures:
    1. Unhandled Flask exceptions
    2. ALL relevant HTTP error responses (4xx / 5xx)
    """

    # --------------------------------------------------
    # 1️⃣ Real Flask exceptions
    # --------------------------------------------------
    @got_request_exception.connect_via(app)
    def _handle_exception(sender, exception, **extra):
        capture_exception(exception)

    # --------------------------------------------------
    # 2️⃣ HTTP outcome-based failures
    # --------------------------------------------------
    @app.after_request
    def _after_request(response):
        try:
            status = response.status_code

            # capture ALL operationally relevant failures
            if status in (400, 401, 403, 404, 500, 503):
                payload = base_payload()
                payload.update({
                    "signal_type": "http_error",
                    "status_code": status,
                    "error_type": "HTTPError",
                    "message": (
                        f"{request.method} {request.path} "
                        f"returned HTTP {status}"
                    ),
                    "stack_trace": "",
                    "source": "http"
                })

                send_sync("/v1/sdk/exception", payload)

        except Exception:
            # never impact client app
            pass

        return response
