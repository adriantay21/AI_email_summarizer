import os
import base64
from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def send_email(sender, to, subject, html_content):
    """Send an email via Gmail API."""
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:

            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:

        service = build('gmail', 'v1', credentials=creds)


        message = MIMEText(html_content, 'html')
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()

        print(f"Email sent successfully! Message ID: {sent_message['id']}")

    except Exception as e:
        print(f"An error occurred: {e}")

def main():

    sender_email = 'testingapi17@gmail.com'
    receiver_email = 'adriantay21@gmail.com'
    email_subject = 'Summarizer Test'

    html_file_path = 'C:\\Users\\adria\OneDrive\\Desktop\\Github repos\\AI_email_summarizer\\output.html'

    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    send_email(sender_email, receiver_email, email_subject, html_content)

if __name__ == '__main__':
    main()
