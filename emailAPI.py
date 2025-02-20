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
from bs4 import BeautifulSoup

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
    date_since = (datetime.now() - timedelta(days=7)).strftime("%d-%b-%Y")
    status, data = mail.search(None, f'(SINCE "{date_since}")')
    print("Login status: ", status)

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
            # Try to extract 'text/html' content first
            for part in email_message.walk():
                content_disposition = str(part.get("Content-Disposition"))
                if part.get_content_type() == 'text/html' and 'attachment' not in content_disposition:
                    charset = part.get_content_charset() or 'utf-8'
                    html_content = part.get_payload(decode=True).decode(charset, errors='replace')
                    # Convert HTML to plain text
                    soup = BeautifulSoup(html_content, 'html.parser')
                    content = soup.get_text()
                    break  # Stop after finding the first 'text/html' part
            else:
                # If no 'text/html' part was found, look for 'text/plain'
                for part in email_message.walk():
                    content_disposition = str(part.get("Content-Disposition"))
                    if part.get_content_type() == 'text/plain' and 'attachment' not in content_disposition:
                        charset = part.get_content_charset() or 'utf-8'
                        content = part.get_payload(decode=True).decode(charset, errors='replace')
                        break  # Stop after finding the first 'text/plain' part
        else:
            # If the email is not multipart
            content_type = email_message.get_content_type()
            charset = email_message.get_content_charset() or 'utf-8'
            payload = email_message.get_payload(decode=True)
            if payload:
                content = payload.decode(charset, errors='replace')
                if content_type == 'text/html':
                    # Convert HTML to plain text
                    soup = BeautifulSoup(content, 'html.parser')
                    content = soup.get_text()

        # Append the extracted email data to the list
        email_data.append({
            "Title": subject,
            "Date": date,
            "Sender_email": sender_email,
            "Sender": sender,
            "Content": content
        })

    # Filter emails from the last 48 hours and by sender
    email_data = last_48_hours(email_data)
    email_data = filter_by_sender(email_data)

    # Write the filtered emails to a JSON file
    with open("emails_last_48_hours.json", "w", encoding="utf-8") as json_file:
        json.dump(email_data, json_file, indent=4, ensure_ascii=False)

    print("Emails from the last 48 hours have been written to 'emails_last_48_hours.json'.")
    return email_data

def last_48_hours(email_data):
    current_time = datetime.now(pytz.UTC)
    last_48_hours = current_time - timedelta(hours=49)  # 1 hour to account for processing time
    filtered_emails = []
    for email in email_data:
        try:
            email_date = parser.parse(email['Date']).astimezone(pytz.UTC)
            if email_date > last_48_hours:
                filtered_emails.append(email)
        except ValueError:
            print(f"Warning: Could not parse date")
    return filtered_emails

def filter_by_sender(email_data):
    filter_emails = os.getenv("FILTER_EMAILS")
    filter_emails = [email.strip() for email in filter_emails.split(',')]
    filtered_emails = []
    for email in email_data:
        if filter_emails and email["Sender_email"].lower() not in [email.lower() for email in filter_emails]:
            continue
        filtered_emails.append(email)
    return filtered_emails

if __name__ == "__main__":
    main()