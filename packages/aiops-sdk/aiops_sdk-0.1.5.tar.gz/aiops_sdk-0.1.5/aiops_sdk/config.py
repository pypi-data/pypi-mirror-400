import os

class Config:
    api_key = None
    service_name = None
    environment = None
    platform_url = None

def load_config(api_key=None):
    Config.api_key = api_key or os.getenv("AIOPS_API_KEY")
    Config.service_name = os.getenv("AIOPS_SERVICE_NAME", "unknown-service")
    Config.environment = os.getenv("AIOPS_ENV", "production")
    Config.platform_url = os.getenv(
        "AIOPS_PLATFORM_URL",
        "https://aiops.1genimpact.cloud"
    )

    if not Config.api_key:
        raise RuntimeError("AIOPS API key is required")
