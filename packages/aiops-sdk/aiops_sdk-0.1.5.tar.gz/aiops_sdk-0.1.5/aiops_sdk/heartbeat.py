from .client import send_async
from .payload import base_payload

def send_heartbeat():
    send_async("/v1/sdk/heartbeat", base_payload())
