from asyncio import run
from scraper import get_event_odds, scrape_events, scrape_leagues
from utils import read_json
import threading

def scrape_odds():
    run(scrape_events())
    loaded_list = read_json('market_ids.json')
    loaded_list = [str(i) for i in loaded_list]
    get_event_odds(loaded_list) 
    
    
def start_console():
    while True:
        cmd = input("Type --help for help: ").lower().strip()

        if cmd == "--help":
            print("Commands: \n"
                  "full: Scrape leagues and get odds\n"
                  "leagues: Scrape all leagues\n"
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
            try:
                while True:
                    scrape_odds()
            except KeyboardInterrupt:
                print("Loop stopped.")
        else:
            print("Unknown command, type --help for help.")


if __name__ == '__main__':

    start_console()
