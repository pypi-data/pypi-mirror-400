from .config import load_config
from .exceptions import register_exception_hook, capture_exception
from .scheduler import start_heartbeat
from .logging_hook import attach_logging_handler
from .version import __version__

def init(api_key=None):
    load_config(api_key)
    register_exception_hook()
    attach_logging_handler()
    start_heartbeat()

def init_flask(app):
    from .integrations.flask import init_flask as _init
    _init(app)
