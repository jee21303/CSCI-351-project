import socket
import threading
import os

MAILBOX_DIR = "mailbox"

class SMTPServer:
    def __init__(self, host="127.0.0.1", port=2525):
        self.host = host
        self.port = port
        os.makedirs(MAILBOX_DIR, exist_ok=True)

    def save_email(self, recipient, sender, message, filename):
        recipient_dir = os.path.join(MAILBOX_DIR, recipient)
        os.makedirs(recipient_dir, exist_ok=True)

        email_path = os.path.join(recipient_dir, f"{filename}.txt")

        with open(email_path, "w") as f:
            f.write(f"From: {sender}\nTo: {recipient}\n\n{message}")

        print(f"Email saved to {email_path}")

    def handle_client(self, conn, addr):
        conn.send(b"220 SimpleSMTP Server Ready\r\n")
        sender = recipient = filename = None
        message_data = []
        state = "INIT"

        while True:
            data = conn.recv(1024).decode().strip()
            if not data:
                break

            print(f"Client: {data}")

            if data.startswith("HELO"):
                conn.send(b"250 Hello\r\n")
                state = "GREETED"

            elif data.startswith("MAIL FROM:") and state == "GREETED":
                sender = data.split(":")[1].strip()
                conn.send(b"250 OK\r\n")
                state = "MAIL FROM SET"

            elif data.startswith("RCPT TO:") and state == "MAIL FROM SET":
                recipient = data.split(":")[1].strip()
                conn.send(b"250 OK\r\n")
                state = "RCPT TO SET"

            elif data.startswith("DATA") and state == "RCPT TO SET":
                conn.send(b"354 End with '.' on a new line\r\n")
                state = "WAITING FOR FILENAME"

            elif state == "WAITING FOR FILENAME" and data.startswith("FILENAME:"):
                filename = data.split(":")[1].strip()
                message_data = []
                state = "DATA"  # Switch to message collection mode

            elif state == "DATA":
                if data == ".":
                    if sender and recipient and filename:
                        self.save_email(recipient, sender, ''.join(message_data), filename)
                        conn.send(b"250 Message accepted\r\n")
                    else:
                        conn.send(b"500 Error: Missing sender, recipient, or filename\r\n")
                    state = "GREETED"  # Reset state for new commands
                else:
                    message_data.append(data + "\n")
            
            elif data.startswith("LIST EMAILS:"):
                recipient = data.split(":")[1].strip()
                recipient_dir = os.path.join(MAILBOX_DIR, recipient)

                if os.path.exists(recipient_dir):
                    emails = os.listdir(recipient_dir)
                    if emails:
                        response = "\n".join(emails) + "\r\n"
                        conn.send(f"250 List of emails for {recipient}:\r\n{response}".encode())
                    else:
                        conn.send(("250 No emails found for " + recipient + "\r\n").encode())
                else:
                    conn.send(b"500 Error: Recipient mailbox not found\r\n")

            elif data.startswith("READ EMAIL:"):
                # Extract the recipient and email filename from the command
                parts = data.split(":")
                if len(parts) == 3:
                    recipient = parts[1].strip()
                    filename = parts[2].strip()

                    recipient_dir = os.path.join(MAILBOX_DIR, recipient)
                    email_path = os.path.join(recipient_dir, f"{filename}.txt")

                    # Check if the email file exists
                    if os.path.exists(email_path):
                        with open(email_path, "r") as f:
                            email_content = f.read()
                            # Send the email content back to the client
                            response = f"250 Email content:\r\n{email_content}\r\n"
                            conn.send(response.encode())
                    else:
                        # If the email file does not exist, notify the client
                        conn.send(f"500 Error: Email {filename} not found for {recipient}\r\n".encode())
                else:
                    conn.send(b"500 Error: Invalid command format for reading email\r\n")

            elif data == "QUIT":
                conn.send(b"221 Bye\r\n")
                break

            else:
                conn.send(b"500 Syntax error\r\n")

        conn.close()

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"SMTP Server running on {self.host}:{self.port}")

        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=self.handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    server = SMTPServer()
    server.start()
