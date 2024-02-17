import json
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from utils import get_ajax_url


async def fetch_html(page, url):
    await page.goto(url)
    html_code = await page.content()
    return html_code

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

        with open('leagues_data.json', 'r') as file:
            sports = json.load(file)

        all_market_ids = []

        for sport in sports:
            print(f"-- {sport['name']}")
            leagues = sport["leagues"]
            markets = sport["markets"]
            for league in leagues:
                for market in markets:
                    print(f"\tLeague: {league['name']} - {market}")

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

        file_path = 'market_ids.json'

        # Remove duplicates
        all_market_ids = list(dict.fromkeys(all_market_ids))
        # Write the list to a JSON file
        with open(file_path, 'w') as json_file:
            json.dump(all_market_ids, json_file)

        print(f'The list of markets has been saved to {file_path}')
