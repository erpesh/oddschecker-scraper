from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from utils import fetch_html, get_full_url, is_date_past, process_json_data, write_json, read_json
from asyncio import run
from utils import read_json
import json

import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from utils import split_list, get_full_url, write_json
from settings.exceptions import exception_bookmakers

from playwright.async_api import async_playwright

from utils import get_ajax_url, read_json, write_json



def scrape_leagues():
    sports = read_json('settings/sports.json')
    sports_with_leagues = []

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)

        for sport in sports:
            sport_leagues = []
            url = get_full_url(sport["url"])

            page = browser.new_page()
            page.goto(url)

            # Wait for the page to load
            page.wait_for_load_state('load', timeout=20000)
            page_source = page.content()

            # Parse the HTML with BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')

            leagues = soup.find_all('li', class_='card-link')
            for league in leagues:
                anchor = league.find('a', href=True)
                league_url = get_full_url(anchor.get('href'))
                league_name = anchor.find(string=True, recursive=False)
                sport_leagues.append({'name': league_name, 'url': league_url})

            sports_with_leagues.append({
                **sport,
                "leagues": sport_leagues
            })
            # Close the current page
            page.close()

        # Close the browser
        browser.close()

    output_file = 'leagues_data.json'
    write_json(output_file, sports_with_leagues, indent=2)

    print(f"Data has been saved to {output_file}")

def get_league_market_ids(json_data, new_bet_data=None):
    # Group by marketId
    grouped_data = {}
    for oc_bet_id, bet_data in json_data.items():
        market_id = bet_data["marketId"]
        if market_id not in grouped_data:
            grouped_data[market_id] = []
        cut_bet_data = {
            "ocBetId": bet_data["ocBetId"],
            "betName": bet_data["betName"]
        }
        grouped_data[market_id].append(cut_bet_data)

    if new_bet_data:
        for bet_id, bet_data in new_bet_data.items():
            decimal_odd = bet_data.get("decimal")

            # Find the corresponding ocBetId in the grouped data
            for market_id, market_bets in grouped_data.items():
                for oc_bet_data in market_bets:
                    if oc_bet_data["ocBetId"] == int(bet_id):
                        # Add the decimal odd to the existing data
                        oc_bet_data["decimal"] = decimal_odd
                        oc_bet_data["bookmakerCodes"] = bet_data["bookmakerCodes"]

    # Create a new dictionary with only valid items
    grouped_data = {key: value for key, value in grouped_data.items() if all('decimal' in item for item in value)}
    return [str(i) for i in grouped_data.keys()]

async def scrape_events():
    async with async_playwright() as p:
        browser = await p.firefox.launch()
        context = await browser.new_context()
            
        sports = read_json('leagues_data.json')

        all_market_ids = []

        for sport in sports:
            leagues = sport["leagues"]
            markets = sport["markets"]
            for league in leagues:
                for market in markets:
                    print(f"\t{sport['name']}: {league['name']} - {market}")

                    try:
                        league_url = get_ajax_url(league['url'], market)

                        page = await context.new_page()
                        html = await fetch_html(page, league_url)

                        soup = BeautifulSoup(html, 'html.parser')

                        scr = soup.find("script", {'data-hypernova-key': "competitionsaccumulatormatches"})
                        if scr:
                            string_script = str(scr)
                            start_index = string_script.find('<!--')
                            end_index = string_script.find('-->')
                            json_data = string_script[start_index + 4:end_index]
                            data = json.loads(json_data)
                            leagues_market_ids = get_league_market_ids(data["bets"]["entities"],
                                                                       data["bestOdds"]["entities"])
                        else:
                            league_matches = soup.find_all("tr", {'class': "match-on"})
                            leagues_market_ids = [i["data-mid"] for i in league_matches]

                        await page.close()
                        all_market_ids.extend(leagues_market_ids)
                    except Exception:
                        print(Exception.__name__)
                        print(f"Something went wrong when fetching {league['name']}")

        await context.close()
        await browser.close()

        # Remove duplicates
        all_market_ids = list(dict.fromkeys(all_market_ids))
        # Write the list to a JSON file
        file_path = 'market_ids.json'
        write_json(file_path, all_market_ids)

        print(f'The list of markets has been saved to {file_path}')
   
def scrape_odds():
    run(scrape_events())
    loaded_list = read_json('market_ids.json')
    loaded_list = [str(i) for i in loaded_list]
    get_event_odds(loaded_list) 
        
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