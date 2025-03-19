import socket
import sys
import time

class SMTPClient:
    def __init__(self, server_host="127.0.0.1", server_port=2525):
        self.server_host = server_host
        self.server_port = server_port

    def send_email(self, sender, recipient, message, filename):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.server_host, self.server_port))

        def recv_response():
            return client_socket.recv(1024).decode().strip()

        print("Server:", recv_response())  # 220 Hello

        client_socket.send(b"HELO client\r\n")
        print("Server:", recv_response())  # 250 OK

        client_socket.send(f"MAIL FROM: {sender}\r\n".encode())
        print("Server:", recv_response())  # 250 OK

        client_socket.send(f"RCPT TO: {recipient}\r\n".encode())
        print("Server:", recv_response())  # 250 OK

        client_socket.send(b"DATA\r\n")
        print("Server:", recv_response())  # 354 Start mail input

        client_socket.send(f"FILENAME: {filename}\r\n".encode())  # Send filename first
        client_socket.send(f"{message}\r\n".encode())  # Send message body
        # Short delay so that the "." isn't combined with the message
        time.sleep(0.1)
        client_socket.send(b".\r\n")
        print("Server:", recv_response())  # 250 Message accepted

        client_socket.send(b"QUIT\r\n")
        print("Server:", recv_response())  # 221 Bye

        client_socket.close()

    def list_emails(self, recipient):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.server_host, self.server_port))

        # Send LIST EMAILS command
        client_socket.send(f"LIST EMAILS: {recipient}\r\n".encode())

        # Receive the server's response and print it
        response = client_socket.recv(1024).decode().strip()
        print("Server:", response)

        # Keep the connection open until the response is fully received
        while response:
            response = client_socket.recv(1024).decode().strip()
            if response:
                print("Server:", response)
                break

        client_socket.close()

    def read_email():
        pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python smtp_client.py send <sender> <recipient> <message> <filename>")
        print("  python smtp_client.py list <recipient>")
        print("  python smtp_client.py read <recipient> <filename>")
        sys.exit(1)

    client = SMTPClient()

    command = sys.argv[1]

    if command == "send" and len(sys.argv) == 6:
        sender = sys.argv[2]
        recipient = sys.argv[3]
        message = sys.argv[4]
        filename = sys.argv[5]
        client.send_email(sender, recipient, message, filename)