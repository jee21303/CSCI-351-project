import socket
import threading
import os

MAILBOX_DIR = "mailbox"

class SMTPServer:
    def __init__(self, host="127.0.0.1", port=2525):
        self.host = host
        self.port = port
        os.makedirs(MAILBOX_DIR, exist_ok=True)

    def save_email():
        pass

    def handle_client():
        pass

    def start():
        pass

if __name__ == "__main__":
    pass
