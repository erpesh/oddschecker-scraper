from asyncio import run
import odds
from events import scrape_events
from leagues import scrape_leagues
from utils import read_json

def scrape_odds():
    run(scrape_events())
    loaded_list = read_json('market_ids.json')
    loaded_list = [str(i) for i in loaded_list]
    odds.get_event_odds(loaded_list)
    

if __name__ == '__main__':
    cmd = input("Type --help for help: ").lower().strip()

    if cmd == "--help":
        print("Commands: \n"
              "full: Scrape leagues and get odds\n"
              "leages: Scrape all leagues\n"
              "odds: Get arbitrage bets once\n"
              "odds-loop: Get arbitrage bets in a loop\n")
    elif cmd == "full":
        scrape_leagues()
        scrape_odds()
    elif cmd == "leagues":
        scrape_leagues()
    elif cmd == "odds":
        scrape_odds()
    elif cmd == "odds-loop":
        print("Press Ctrl+C to stop the loop")
        while True:
            scrape_odds()
