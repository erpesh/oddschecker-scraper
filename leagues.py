from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from utils import get_full_url, write_json, read_json

sports = read_json('settings/sports.json')

def scrape_leagues():
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

