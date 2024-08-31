import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd


def get_full_url(url: str):
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return "https://www.oddschecker.com/" + url


def get_ajax_url(link: str, market: str):
    if "https://www.oddschecker.com/" in link:
        link = link.replace("https://www.oddschecker.com/", "")
    return f"https://www.oddschecker.com/ajax/cards-default/{link}?market={market}"


def split_list(input_list: list[str], max_chunk_size: int) -> list[list[str]]:
    # Calculate the number of chunks needed
    num_chunks = -(-len(input_list) // max_chunk_size)

    # Use a list comprehension to create the chunks
    chunks = [input_list[i * max_chunk_size:(i + 1) * max_chunk_size] for i in range(num_chunks)]

    return chunks

def write_json(file_name: str, content: object, **kwargs):
    with open(file_name, 'w') as json_file:
        json.dump(content, json_file, **kwargs)
        
def read_json(file_name: str):
    with open(file_name, 'r') as json_file:
        return json.load(json_file)
    
def is_date_past(date_string):
    date_object = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
    current_datetime = datetime.now()
    return date_object < current_datetime or date_object > current_datetime.today() + relativedelta(months=1)

def process_json_data(json_data):
    write_json("event_odds.json", json_data)

    df = pd.DataFrame(json_data)

    # Specify the Excel file name (including the extension .xls)
    excel_file_name = "odds.csv"

    # Write DataFrame to Excel file
    df.to_csv(excel_file_name, index=False)
    
async def fetch_html(page, url):
    await page.goto(url)
    html_code = await page.content()
    return html_code