import threading
import time
from .heartbeat import send_heartbeat

def start_heartbeat(interval=30):
    def _run():
        while True:
            send_heartbeat()
            time.sleep(interval)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
