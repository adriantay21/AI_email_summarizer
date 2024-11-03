import imaplib
import email
from email.header import decode_header
import json
import dotenv
import os
from datetime import datetime, timedelta
import pytz
import re
from dateutil import parser

dotenv.load_dotenv()


imap_server = os.getenv("IMAP_SERVER")
email_address = os.getenv("EMAIL_ADDRESS")
email_password = os.getenv("EMAIL_PASSWORD")

def main():
    mail = imaplib.IMAP4_SSL(imap_server)

    mail.login(email_address, email_password)

    # Select the mailbox (inbox in this case)
    mail.select('inbox')

    # Search for emails
    status, data = mail.search(None, 'ALL')

    # Get the list of email IDs
    email_ids = data[0].split()

    # Loop through the email IDs and fetch the email data
    email_data = []
    for email_id in email_ids:
        # Fetch the email message by ID
        status, data = mail.fetch(email_id, '(RFC822)')
        raw_email = data[0][1]

        # Convert raw email bytes to a message object
        email_message = email.message_from_bytes(raw_email)

        # Decode the email sender
        from_header = decode_header(email_message.get('From'))
        sender = ''
        for part in from_header:
            decoded_string, charset = part
            if isinstance(decoded_string, bytes):
                charset = charset or 'utf-8'
                decoded_string = decoded_string.decode(charset, errors='replace')
            sender += decoded_string
            sender_email = sender.split()[-1].strip('<>')
            sender = sender.split('<')[0].strip()

        # Decode the email date
        date_header = decode_header(email_message.get('Date'))
        date = ''
        for part in date_header:
            decoded_string, charset = part
            if isinstance(decoded_string, bytes):
                charset = charset or 'utf-8'
                decoded_string = decoded_string.decode(charset, errors='replace')
            date += decoded_string

        # Decode the email subject
        subject_header = decode_header(email_message.get('Subject'))
        subject = ''
        for part in subject_header:
            decoded_string, charset = part
            if isinstance(decoded_string, bytes):
                charset = charset or 'utf-8'
                decoded_string = decoded_string.decode(charset, errors='replace')
            subject += decoded_string

        # Initialize the content variable
        content = ''

        # Extract the email content
        if email_message.is_multipart():
            # Iterate over email parts
            for part in email_message.walk():
                # If the content type is text/plain
                if part.get_content_type() == 'text/plain':
                    charset = part.get_content_charset() or 'utf-8'
                    content = part.get_payload(decode=True).decode(charset, errors='replace')
                    break  # Stop after finding the first text/plain part
        else:
            # If the email is not multipart
            charset = email_message.get_content_charset() or 'utf-8'
            content = email_message.get_payload(decode=True).decode(charset, errors='replace')

        
        # Print the extracted information
        print('From:', sender)
        print('Date:', date)
        print('Subject:', subject)
        print('Content:', content)
        print('-' * 50)
        email_data.append({
        "Title": subject,
        "Date": date,
        "Sender_email": sender_email,
        "Sender": sender,
        "Content": content
        })       
        email_data = last_48_hours(email_data)
        email_data = filter_by_sender(email_data)
    with open("emails_last_48_hours.json", "w", encoding="utf-8") as json_file:
        json.dump(email_data, json_file, indent=4, ensure_ascii=False)

    print("Emails from the last 48 hours have been written to 'emails_last_48_hours.json'.")


def last_48_hours(email_data):
    current_time = datetime.now(pytz.UTC)
    last_48_hours = current_time - timedelta(hours=49) # 1 hour to account for processing time
    filtered_emails = []
    for email in email_data:
        try:
            email_date = parser.parse(email['Date']).astimezone(pytz.UTC)
            if email_date > last_48_hours:
                filtered_emails.append(email)
        except ValueError:
            print(f"Warning: Could not parse date: {email['Date']}")
    return filtered_emails

def filter_by_sender(email_data):

    filter_emails = []
    filter_emails = os.getenv("FILTER_EMAILS")
    print(filter_emails)
    filter_emails = [email.strip() for email in filter_emails.split(',')]
    filtered_emails = []
    for email in email_data:
        if filter_emails and email["Sender_email"].lower() not in [email.lower() for email in filter_emails]:
            continue
        filtered_emails.append(email)
    return filtered_emails
    

if __name__ == "__main__":
    main()