from datetime import datetime
from dateutil.relativedelta import relativedelta
import json

import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from utils import split_list, get_full_url, write_json

exception_bookmakers = [
    "LS", # LiveScore
    "OE", # 10bet
    "WH", # WilliamHill
    "SK", # Skybet
    "PP", # PaddyPower
    "FB", # BetFair
    "VT", # VBet
    "S6", # StarSports
    "SI", # SportingIndex
    "SX", # SpreadEx
    "WA", # Betway
    "VC", # BetVictor - BANNED
    "QN", "G5", # QuinnBet + BetGoodWin
    'KN', 'UN', 'DP', # Unibet-alike,
    "BY", # BoyleSports - BANNED

]


def is_date_past(date_string):
    date_object = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
    current_datetime = datetime.utcnow()
    return date_object < current_datetime or date_object > current_datetime.today() + relativedelta(months=1)

def get_event_odds(market_ids: list[str]):
    market_ids_2d = split_list(market_ids, 100)

    with sync_playwright() as p:
        browser = p.firefox.launch()
        context = browser.new_context()
        page = context.new_page()

        odds_data = []

        for ids_chunk in market_ids_2d:
            ids_str = ",".join(ids_chunk)
            api_url = get_full_url(f"api/markets/v2/all-odds?market-ids={ids_str}&repub=OC")

            # Navigate to the API URL
            page.goto(api_url)

            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            json_content = soup.find('pre').text
            # print(json_content)
            # Process the JSON data as needed
            chunk_data = json.loads(json_content)
            odds_data.extend(chunk_data)

        write_json("odds_data.json", odds_data, indent=2)

        formatted_odds_data = []
        for odd in odds_data:

            is_running = "In Running" in odd["subeventName"]
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

        # Close the browser
        browser.close()
        process_json_data(formatted_odds_data)


def process_json_data(json_data):
    write_json("event_odds.json", json_data)

    df = pd.DataFrame(json_data)

    # Specify the Excel file name (including the extension .xls)
    excel_file_name = "odds.csv"

    # Write DataFrame to Excel file
    df.to_csv(excel_file_name, index=False)
