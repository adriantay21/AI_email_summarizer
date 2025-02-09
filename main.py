import sys
import time
from datetime import timedelta
from gptapi import summarize_emails, process_html
from sendemail import main as send_summary_email
from emailAPI import main as fetch_emails
def run_main_script():
    try:
        print("Fetching emails with emailAPI.py...")
        fetch_emails()
        print("Emails fetched successfully.\n")

        print("Summarizing emails with gptapi.py...")
        emails_summary = summarize_emails()
        print("Emails summarized successfully.\n")

        print("Generating HTML...")
        process_html(emails_summary)
        print("Emails summarized and HTML generated.\n")

        print("Sending summary email with sendemail.py...")
        send_summary_email()
        print("Summary email sent successfully.\n")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

def countdown(hours):
    for hour in range(hours, 0, -1):
        print(f"{hour} hour(s) left until the script runs...")
        time.sleep(3600)  # Wait for 1 hour (3600 seconds)

if __name__ == "__main__":
    while True:
        run_main_script()

        countdown(48)  # Wait for 48 hours before running again

