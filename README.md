# CSCI-351 Project: SMTP Email Server

## How To Compile:
There are no dependencies for this assignment.\
You need to run the email server and then the client in two separate commend prompt windows.\
To run the program, go to the CSCI-351-project directory in each window and enter:\
First window: python smtp_server.py\
Second window: python smtp_client.py [args]


## Arguments (smtp_server.py)
* None

## Arguments (smtp_client.py)
* Send email mode
    * send: Use send email mode
    * [sender]\: The sender of the email
    * [recipient]\: The recipient of the email
    * [message]\: The email message, wrapped in quotation marks ("<message\>")
    * [subject]\: The subject of the email, must be one word
* List emails mode
    * list: Use list emails mode
    * [recipient]\: The user whose emails to display
* Read email mode
    * read: Use read email mode
    * [recipient]\: The user whose email to read
    * [subject]:\ The subject of the email to read

## Examples

This Command will start the SMTP email server:
###
    python smtp_server.py
This command will send an email from alice@example.com to bob@example.com with
message contents "test email" and the subject test_email:
###
    python smtp_client.py send alice@example.com bob@example.com "test email" test_email
This command will list all emails in bob@example.com's mailbox
###
    python smtp_client.py list bob@example.com
This command will dipslay the message in bob@example.com's mailbox with the subject test_email
###
    python smtp_client.py read bob@example.com test_email
    
## Other Notes
* Upon receiving an email, the server will save it in the mailbox directory
    * This directory must be present for the program to work, do not delete it
    * Each user will have a subdirectory within mailbox for their respective emails
* Emails are saved with the subject as the filename instead of a timestamp for         simplicity and readability, meaning a user cannot have 2 emails with the same subject in their inbox
* If an email is sent to a user who does not have an inbox set up, one will be generated when the email is received
* If you request the list of emails from a nonexistent user, you will get an error
* If you request an email message's contents but that email does not exist, you will get an error
* Read the report for a more in-depth explanation of implementation decisions and comparison to the real SMTP protocol
