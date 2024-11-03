import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import dotenv
from datetime import date, timedelta

dotenv.load_dotenv()
smtp_server = os.getenv('SMTP_SERVER')
email_address = os.getenv('EMAIL_ADDRESS')
email_password = os.getenv('EMAIL_PASSWORD')
receiver_email = os.getenv('RECEIVER_EMAIL')
# Connect to the SMTP server
def send_email(sender_email, receiver_email, email_subject, html_content):

    port = 587
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()


    # Login to the server
    server.login(email_address, email_password)

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = email_subject
    html = MIMEText(html_content, 'html')
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    message.attach(html)

    # Send the email
    server.sendmail(sender_email, receiver_email, message.as_string())

    # Close the connection to the SMTP server
    server.quit()


def main():

    email_subject = 'GPT News Digest for ' + (date.today() - timedelta(days=1)).strftime('%m/%d/%y')

    html_file_path = 'output.html'

    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_file_path = os.path.join(current_dir, html_file_path)

    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    try:
        send_email(email_address, receiver_email, email_subject, html_content)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
