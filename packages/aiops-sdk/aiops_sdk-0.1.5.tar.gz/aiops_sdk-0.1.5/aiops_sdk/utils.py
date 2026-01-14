import socket
import time

def hostname():
    return socket.gethostname()

def timestamp():
    return int(time.time())
