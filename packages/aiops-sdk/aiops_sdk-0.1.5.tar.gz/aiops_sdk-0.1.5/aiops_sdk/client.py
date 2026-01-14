import threading
import requests
from .config import Config

def _post(path, payload):
    requests.post(
        f"{Config.platform_url}{path}",
        json=payload,
        headers={
            "Authorization": f"Bearer {Config.api_key}",
            "Content-Type": "application/json"
        },
        timeout=3
    )

def send_async(path, payload):
    threading.Thread(
        target=_safe_post,
        args=(path, payload),
        daemon=True
    ).start()

def send_sync(path, payload):
    try:
        _post(path, payload)
    except Exception:
        pass

def _safe_post(path, payload):
    try:
        _post(path, payload)
    except Exception:
        pass
