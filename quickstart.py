import os.path
import base64
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_email_content(msg_data):
    """Extracts all text parts of the email (HTML and plain text) and cleans the output."""
    content = ""
    if "parts" in msg_data["payload"]:
        parts = msg_data['payload']['parts']
    else:
        parts = [msg_data["payload"]]  # In case there's no 'parts', treat the payload as a single part

    for part in parts:
        if part['mimeType'] == 'text/html':
            data = part['body'].get('data')
            if data:
                decoded_data = base64.urlsafe_b64decode(data).decode("utf-8")
                soup = BeautifulSoup(decoded_data, 'html.parser')

                # Remove all links and images
                for a in soup.find_all('a'):
                    a.decompose()
                for img in soup.find_all('img'):
                    img.decompose()

                # Get the clean text content from the HTML
                text = soup.get_text(separator=" ")
                content += ' '.join(text.split()) + "\n"  # Replace multiple spaces/newlines with single space

        elif part['mimeType'] == 'text/plain':
            data = part['body'].get('data')
            if data:
                decoded_data = base64.urlsafe_b64decode(data).decode("utf-8")
                content += ' '.join(decoded_data.split()) + "\n"  # Clean plain text

    return content.strip()  # Return cleaned content

def main():
    """Fetches Gmail messages from the last 48 hours and writes them to a JSON file."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # Load the list of email addresses to filter from a JSON file
    filter_emails = []
    if os.path.exists("emails.json"):
        with open("emails.json", "r") as f:
            filter_emails = json.load(f)

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)

        # Calculate the date range for the last 48 hours
        now = datetime.utcnow()
        two_days_ago = now - timedelta(hours=48)
        query = f"after:{int(two_days_ago.timestamp())}"

        # Fetch the emails
        results = service.users().messages().list(userId="me", q=query).execute()
        messages = results.get("messages", [])

        if not messages:
            print("No messages found.")
            return

        # Prepare a list to hold the email data
        email_data = []

        # Loop through the messages and extract details
        for msg in messages:
            msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
            headers = msg_data["payload"]["headers"]
            date = next(header["value"] for header in headers if header["name"] == "Date")
            sender = next(header["value"] for header in headers if header["name"] == "From")
            subject = next(header["value"] for header in headers if header["name"] == "Subject")
            sender_email = sender.split()[-1].strip('<>')

            # If filter is set, skip emails not matching the filter list
            if filter_emails and sender_email.lower() not in [email.lower() for email in filter_emails]:
                continue

            # Extract and decode email content
            content = get_email_content(msg_data)

            # Append the email details to the list
            email_data.append({
                "Title": subject,
                "Date": date,
                "Sender": sender_email,
                "Content": content
            })

        # Write the email data to a JSON file
        with open("emails_last_48_hours.json", "w", encoding="utf-8") as json_file:
            json.dump(email_data, json_file, indent=4, ensure_ascii=False)

        print("Emails from the last 48 hours have been written to 'emails_last_48_hours.json'.")

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()