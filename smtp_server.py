import socket
import threading
import os

MAILBOX_DIR = "mailbox"

class SMTPServer:
    """
    Defines the SMTP Server class
    """
    def __init__(self, host="127.0.0.1", port=2525):
        """
        Create an SMTP Server object
        Inputs:
        host: The server IP address
        port: The server port
        Outputs:
        None
        """
        self.host = host
        self.port = port
        os.makedirs(MAILBOX_DIR, exist_ok=True)

    def save_email(self, recipient, sender, message, filename):
        """
        Save an email to the mailbox directory
        Inputs:
        recipient: Who the email is addressed to
        sender: Who sent the email
        message: The content of the email
        filename: The filename/subject to save the email under
        Outputs:
        None
        """
        # Set the directory to save to
        recipient_dir = os.path.join(MAILBOX_DIR, recipient)
        os.makedirs(recipient_dir, exist_ok=True)
        email_path = os.path.join(recipient_dir, f"{filename}.txt")
        # Write email sender, receiver, and contents to a file
        with open(email_path, "w") as f:
            f.write(f"From: {sender}\nTo: {recipient}\n\n{message}")
        print(f"Email saved to {email_path}")

    def handle_client(self, conn, _):
        """
        Handle client messages
        Inputs:
        conn: The connection with the client
        Outputs:
        None
        """
        # Start server in the initial state
        conn.send(b"220 SimpleSMTP Server Ready\r\n")
        sender = recipient = filename = None
        message_data = []
        state = "INIT"
        # Continuously listen for messages
        while True:
            data = conn.recv(1024).decode().strip()
            if not data:
                break
            print(f"Client: {data}")
            # If HELO signal is received, go to GREETED state
            if data.startswith("HELO"):
                conn.send(b"250 Hello\r\n")
                state = "GREETED"
            # Establish the sender's identity, go to MAIL FROM SET state
            elif data.startswith("MAIL FROM:") and state == "GREETED":
                sender = data.split(":")[1].strip()
                conn.send(b"250 OK\r\n")
                state = "MAIL FROM SET"
            # Establish receiver's identity, go to RCPT TO SET state
            elif data.startswith("RCPT TO:") and state == "MAIL FROM SET":
                recipient = data.split(":")[1].strip()
                conn.send(b"250 OK\r\n")
                state = "RCPT TO SET"
            # Start listening for data, first the filename
            # go to the WAITING FOR FILENAME state
            elif data.startswith("DATA") and state == "RCPT TO SET":
                conn.send(b"354 End with '.' on a new line\r\n")
                state = "WAITING FOR FILENAME"
            # Get the filename, then go back to the DATA state
            elif state == "WAITING FOR FILENAME" and data.startswith("FILENAME:"):
                filename = data.split(":")[1].strip()
                message_data = []
                state = "DATA"
            # Now get the email message contents
            elif state == "DATA":
                # A dot by itself is the signal for end of email message
                if data == ".":
                    # Ensure all necessary details are there, then save the email
                    if sender and recipient and filename:
                        self.save_email(recipient, sender, ''.join(message_data), filename)
                        conn.send(b"250 Message accepted\r\n")
                    else:
                        conn.send(b"500 Error: Missing sender, recipient, or filename\r\n")
                    # Reset state to GREETED and wait for new messages
                    state = "GREETED"
                # If no end signal, keep listening for message content
                else:
                    message_data.append(data + "\n")
            # User requested to list emails for a given address
            elif data.startswith("LIST EMAILS:"):
                recipient = data.split(":")[1].strip()
                recipient_dir = os.path.join(MAILBOX_DIR, recipient)
                # Make sure the user exists
                if os.path.exists(recipient_dir):
                    emails = os.listdir(recipient_dir)
                    # Display email subject lines if any exist
                    if emails:
                        response = "\n".join(emails) + "\r\n"
                        conn.send(f"250 List of emails for {recipient}:\r\n{response}".encode())
                    # If none, simply say there are no emails avvailable
                    else:
                        conn.send(("250 No emails found for " + recipient + "\r\n").encode())
                # If the user doesn't exist, report that issue
                else:
                    conn.send(b"500 Error: Recipient mailbox not found\r\n")
            # User requested to read an individual email
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
                    # Extra error checking
                    conn.send(b"500 Error: Invalid command format for reading email\r\n")
            # End signal when client closes connection
            elif data == "QUIT":
                conn.send(b"221 Bye\r\n")
                break
            # Error if none of the above cases are run
            else:
                conn.send(b"500 Syntax error\r\n")
        conn.close()

    def start(self):
        """
        Start the SMTP server
        Inputs:
        None
        Outputs:
        None
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"SMTP Server running on {self.host}:{self.port}")

        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=self.handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    # Create and start the server
    server = SMTPServer()
    server.start()
