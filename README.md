
<h1 align="center">
  <br>
  <a href="https://github.com/adriantay21/AI_email_summarizer/"><img src="gptmail.png" alt="Markdownify" width="200"></a>
  <br>
  AI Email Summarizer
  <br>
</h1>

<h4 align="center">Another GPT wrapper that summarizes emails into digestible content</a>.</h4>


<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#how-to-use">How To Use</a>
</p>

![screenshot](Gptmail_screenshot.png)

## Key Features

* Pulls and filters emails from the past 48 hours
* Summarizes the email content using the GPT API and categorizes the summarized content
* Reformat the summarized content as html
* Send the html content to a personal mailbox

## How To Use

To clone and run this application, you'll need [Git](https://git-scm.com) and [Python](https://www.python.org/downloads/) installed on your computer. You also need to provide your own OPENAI api key, IMAP and SMTP server addresses.

From your command line:
```sh
# Clone this repository
git clone https://github.com/adriantay21/AI_email_summarizer

# Go into the repository
cd electron-markdownify

# Install required packages
pip install requirements.txt
```

Set these variables in your .env file
```sh
OPENAI_API_KEY=APIKEY
EMAIL_ADDRESS=email@email.com
EMAIL_PASSWORD=password
IMAP_SERVER=imap.xxx.com
SMTP_SERVER=smtp.xxx.com
RECEIVER_EMAIL=email@email.com
```

To run using docker:
```sh
docker pull adriantay21/aiemailsummarizer
docker run -d --name my_container_name adriantay21/dockerimage
```



