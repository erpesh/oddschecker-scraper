import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
from settings.exceptions import exception_bookmakers


def get_full_url(url: str) -> str:
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return "https://www.oddschecker.com/" + url


def get_ajax_url(link: str, market: str) -> str:
    if "https://www.oddschecker.com/" in link:
        link = link.replace("https://www.oddschecker.com/", "")
    return f"https://www.oddschecker.com/ajax/cards-default/{link}?market={market}"


def split_list(input_list: list[str], max_chunk_size: int) -> list[list[str]]:
    # Calculate the number of chunks needed
    num_chunks = -(-len(input_list) // max_chunk_size)

    # Use a list comprehension to create the chunks
    chunks = [input_list[i * max_chunk_size : (i + 1) * max_chunk_size] for i in range(num_chunks)]

    return chunks

def write_json(file_name: str, content: object, **kwargs):
    with open(file_name, 'w') as json_file:
        json.dump(content, json_file, **kwargs)
        
def read_json(file_name: str) -> object:
    with open(file_name, 'r') as json_file:
        return json.load(json_file)
    
def is_date_past(date_string: str) -> bool:
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
    
async def fetch_html(page, url) -> str:
    await page.goto(url)
    html_code = await page.content()
    return html_code

# Temporary. Should be moved to the API side
def find_arbitrage():
    odds_data = read_json("odds_data.json")
    
    formatted_odds_data = []
    for odd in odds_data:

        is_running = "In Running" in odd["subeventName"]
        # We skip the event if it is in running, if it doesn't have the bestOddsBookmakerCodes key, if the date is past or if there are less than 2 bets
        if is_running or any("bestOddsBookmakerCodes" not in bet for bet in odd["bets"]) or is_date_past(odd["subeventStartTime"]) or len(odd["bets"]) < 2:
            continue

        # Filter out exception bookmakers
        for bet in odd["bets"]:
            bet['bestOddsBookmakerCodes'] = [bookmaker for bookmaker in bet['bestOddsBookmakerCodes'] if
                                            bookmaker not in exception_bookmakers]

        
        if any(len(bet["bestOddsBookmakerCodes"]) == 0 for bet in odd["bets"]):
            continue

        if all('bestOddsDecimal' in bet for bet in odd["bets"]):
            bets = [{
                        "name": bet["betName"],
                        "bookmakers": bet["bestOddsBookmakerCodes"],
                        "odd": bet["bestOddsDecimal"]
                    } if "bestOddsDecimal" in bet else None for bet in odd["bets"]]

            total_inverse_odds = sum([1 / bet["odd"] for bet in bets])
            print(odd["bets"], total_inverse_odds)
            if total_inverse_odds != 0 and total_inverse_odds < 1:
                profit_percentage = ((1 / total_inverse_odds) - 1) * 100
                if profit_percentage > 0.5:
                    formatted_odd = {
                        "category": odd["categoryName"],
                        "event": odd["eventName"],
                        "name": odd["subeventName"],
                        "market": odd["marketTypeName"],
                        "date": odd["subeventStartTime"],
                        "bets": bets,
                        "profit": profit_percentage
                    }
                    formatted_odds_data.append(formatted_odd)
    process_json_data(formatted_odds_data)