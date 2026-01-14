# aiops_sdk/payload.py

from .config import Config
from .utils import hostname, timestamp

def base_payload():
    return {
        "service": Config.service_name,
        "environment": Config.environment,
        "host": hostname(),
        "timestamp": timestamp(),

        # 🔴 normalized fields (always present)
        "signal_type": None,
        "status_code": None
    }
