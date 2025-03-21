import socket
import sys
import time

class SMTPClient:
    def __init__(self, server_host="127.0.0.1", server_port=2525):
        self.server_host = server_host
        self.server_port = server_port

    def send_email(self, sender, recipient, message, filename):
        """
        Send an email to the mail server
        Inputs:
        sender: The sender of the email
        recipient: The recipient of the email
        message: The email message
        filename: The filename/subject to save the email under
        Outputs:
        None
        """
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.server_host, self.server_port))
        def recv_response():
            """
            Receive a response from the server
            Inputs:
            None
            Outputs:
            The message content
            """
            return client_socket.recv(1024).decode().strip()
        # Establish initial connection (220 HELO)
        print("Server:", recv_response())
        client_socket.send(b"HELO client\r\n")
        print("Server:", recv_response())
        # Establish Sender
        client_socket.send(f"MAIL FROM: {sender}\r\n".encode())
        print("Server:", recv_response())
        # Establish Recipient
        client_socket.send(f"RCPT TO: {recipient}\r\n".encode())
        print("Server:", recv_response())
        # Prepare for sending data (354 Start mail input)
        client_socket.send(b"DATA\r\n")
        print("Server:", recv_response())
        # Send the subject/filename, then the message content, then the end signal
        client_socket.send(f"FILENAME: {filename}\r\n".encode())
        client_socket.send(f"{message}\r\n".encode())
        # Short delay so that the "." isn't combined with the message
        time.sleep(0.1)
        client_socket.send(b".\r\n")
        print("Server:", recv_response())
        # Send end signal (221 Bye)
        client_socket.send(b"QUIT\r\n")
        print("Server:", recv_response())
        client_socket.close()

    def list_emails(self, recipient):
        """
        Request all availiable emails for a user
        Inputs:
        recipient: The user whose emails to view
        Outputs:
        None
        """
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.server_host, self.server_port))
        # Send LIST EMAILS request
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


    def read_email(self, recipient, email_filename):
        """
        Request the message contents of a single email
        Inputs:
        recipient: The user that the email is addressed to
        email_filename: The subject/filename the email is saved under
        """
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.server_host, self.server_port))
        # Send READ EMAIL request
        client_socket.send(f"READ EMAIL: {recipient}: {email_filename}\r\n".encode())
        response = client_socket.recv(1024).decode().strip()
        print("Server:", response)
        # Keep the connection open until the response is fully received
        while response:
            response = client_socket.recv(1024).decode().strip()
            if response:
                print("Server:", response)
                break
        client_socket.close()

if __name__ == "__main__":
    # Input validation
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
    elif command == "list" and len(sys.argv) == 3:
        recipient = sys.argv[2]
        client.list_emails(recipient)
    elif command == "read" and len(sys.argv) == 4:
        recipient = sys.argv[2]
        filename = sys.argv[3]
        client.read_email(recipient, filename)
    else:
        print("Invalid command or missing arguments.")
        sys.exit(1)
