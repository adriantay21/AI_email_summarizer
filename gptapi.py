import json
from openai import OpenAI
import os
import re
from pydantic import BaseModel
from datetime import datetime

if os.path.exists("openaikey.json"):
    with open("openaikey.json", "r") as f:
        os.environ["OPENAI_API_KEY"] = json.load(f)["token"]

client = OpenAI()

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Use os.path.join for cross-platform compatibility
emails_path = os.path.join(current_dir, "emails_last_48_hours.json")
summarizer_prompt_path = os.path.join(current_dir, "summarizer_system_prompt.txt")

with open(emails_path, "r", encoding="utf-8") as file:
    emails = json.load(file)

# Read the summarizer system prompt
with open(summarizer_prompt_path, "r", encoding="utf-8") as file:
    summarizer_system_prompt = file.read()



class summary_format(BaseModel):
    economic_news: list[str]
    personal_finance: list[str]
    technology_and_science: list[str]
    financial_news: list[str]
    cryptocurrency_news: list[str]
    other: list[str]

def query_gpt(instruction, message, temperature, model, response_format):
    if model == "gpt-4o-mini":
        input_pricing = 0.15 / 1000000
        output_pricing = 0.6 / 1000000
    elif model == "gpt-4o":
        input_pricing = 5 / 1000000
        output_pricing = 15 / 1000000
    elif model == "o1-mini":
        input_pricing = 3 / 1000000
        output_pricing = 12 / 1000000
    else:
        print("model invalid...")
        return None, None, None, None, None

    response = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": [{"type": "text", "text": instruction}]},
            {"role": "user", "content": [{"type": "text", "text": message}]}
        ],
        store=True,
        temperature=temperature,
        max_tokens=2000,
        frequency_penalty=0,
        presence_penalty=0,
        seed=0,
        response_format=response_format
    )

    output = response.model_dump()
    answer = output['choices'][0]['message']['content']
    usage = output['usage']
    completion_tokens = usage['completion_tokens']
    prompt_tokens = usage['prompt_tokens']
    input_tokens_cost = prompt_tokens * input_pricing
    output_tokens_cost = completion_tokens * output_pricing

    return answer, prompt_tokens, completion_tokens, input_tokens_cost, output_tokens_cost

def summarize_emails():
    index = 0
    emails_dict = {}
    emails_dict_list = []
    for email in emails:
        index += 1
        email_content = str(email['Content'])  
        email_content = re.sub(r'[^\w\s]', '', email_content)
        sender = email['Sender'] 

        date = email['Date']
        # Remove the timezone abbreviation in parentheses
        date = re.sub(r'\s*\([A-Z]+\)$', '', date)
        parsed_date = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %z')
        formatted_date = parsed_date.strftime('%m/%d')
        date = formatted_date
        
        email_content = "Content: " + email_content
        answer, prompt_tokens, completion_tokens, input_tokens_cost, output_tokens_cost = query_gpt(
            summarizer_system_prompt, email_content, 0.4, "gpt-4o", summary_format
        )
        print(answer, prompt_tokens, completion_tokens, input_tokens_cost, output_tokens_cost)

        answer_dict = json.loads(answer)

        for key in answer_dict:
            # Append sender to updates, but not to no update messages
            answer_dict[key] = [
                s if "updates related to this section" in s.strip().lower() else s + f" ({sender} - {date})"
                for s in answer_dict[key]
            ]
        emails_dict_list.append(answer_dict)
    
    keys = emails_dict_list[0].keys()

    for key in keys:
        combined_list = []
        for d in emails_dict_list:
            combined_list.extend(d[key])
        # Remove duplicates
        combined_list = list(set(combined_list))
        # Check if all items are 'no updates' messages
        if all("updates related to this section" in item.strip().lower() for item in combined_list):
            combined_list = ["There were no updates related to this section."]
        else:
            # Remove any 'no updates' messages
            combined_list = [item for item in combined_list if "updates related to this section" not in item.strip().lower()]
        emails_dict[key] = combined_list

    return emails_dict

def process_html(emails_dict):

    section_titles = {
        "economic_news": "Economic News",
        "personal_finance": "Personal Finance",
        "technology_and_science": "Technology & Science",
        "financial_news": "Financial News",
        "cryptocurrency_news": "Cryptocurrency News",
        "other": "Other News"
    }

    html_content = '''<!DOCTYPE html>
    <html lang="en">

    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News Report</title>
    <link rel="stylesheet" href="https://stackedit.io/style.css">
    </head>

    <body class="stackedit">
    <div class="stackedit__html">
    '''

    for key in section_titles:
        html_content += f'    <h1 id="{key.replace("_", "-")}">{section_titles[key]}</h1>\n'
        html_content += '    <ul>\n'

        items = emails_dict.get(key, ["There were no updates related to this section"])
        if not items:
            items = ["There were no updates related to this section"]
        
        for item in items:
            html_content += '      <li>\n'

            if item.strip().lower() == "there were no updates related to this section":
                html_content += '        <p>There were no updates related to this section.</p>\n'
            else:
                # Split the item into a headline and content if applicable
                if ':' in item:
                    headline, content = item.split(':', 1)
                    html_content += f'        <p><strong>{headline.strip()}:</strong>{content.strip()}</p>\n'
                else:
                    html_content += f'        <p>{item.strip()}</p>\n'

            html_content += '      </li>\n'

        html_content += '    </ul>\n\n'

    html_content += '  </div>\n</body>\n\n</html>'

    with open(f"C:\\Users\\adria\\OneDrive\\Desktop\\Github repos\\AI_email_summarizer\\output.html", 'w', encoding='utf-8') as file:
        file.write(html_content)

    print("HTML content has been written to 'output.html'.")

def main():
    emails_dict = summarize_emails()
    return process_html(emails_dict)
    

if __name__ == '__main__':
    main()