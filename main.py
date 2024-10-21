import sys
from quickstart import main as fetch_emails
from gptapi import summarize_emails, process_html
from sendemail import main as send_summary_email

def main():
    try:
        print("Fetching emails with quickstart.py...")
        fetch_emails()
        print("Emails fetched successfully.\n")

        print("Summarizing emails with gptapi.py...")
        emails_summary = summarize_emails() 
        process_html(emails_summary)  
        print("Emails summarized and HTML generated.\n")


        print("Sending summary email with sendemail.py...")
        send_summary_email() 
        print("Summary email sent successfully.\n")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)  

if __name__ == "__main__":
    main()
