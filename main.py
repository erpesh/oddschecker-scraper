# from leagues import scrape_leagues
# scrape_leagues()
import json
from asyncio import run

import requests

import odds
from events import scrape_events
from leagues import scrape_leagues

if __name__ == '__main__':
    # scrape_leagues()
    while True:
        run(scrape_events())
        with open('market_ids.json', 'r') as json_file:
            loaded_list = json.load(json_file)
        loaded_list = [str(i) for i in loaded_list]
        odds.get_event_odds(loaded_list)
