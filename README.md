# Arbitrage Betting Finder

This Python application is designed to help users find arbitrage betting opportunities by scraping odds from [oddschecker.com](https://www.oddschecker.com/). Arbitrage betting is a strategy where a bettor places bets on all possible outcomes of an event at odds that guarantee profit, regardless of the event's outcome.

## Features

- **Data Scraping:** Automatically scrapes betting odds from oddschecker.com for various sports and events.
- **Arbitrage Detection:** Analyzes the scraped data to identify arbitrage betting opportunities.
- **User-Friendly:** Easy to use, requiring minimal setup and input from the user.
- **Customizable:** Users can specify particular sports or events they are interested in for more targeted results.

## How It Works

1. **Data Collection:** The script starts by scraping oddschecker.com for the latest betting odds across different sports and events.
2. **Analysis:** It then analyzes the collected data to find combinations of odds that present arbitrage opportunities.
3. **Notification:** Once an arbitrage opportunity is identified, the script alerts the user with details of the bet to place, including which bookmakers to use and the suggested amount to bet.

## Getting Started

To use this application, follow these steps:

1. Ensure you have Python installed on your system.
2. Clone this repository to your local machine.
3. Install the required Python packages by running `pip install -r requirements.txt` in your terminal.
4. Run the script with `python main.py`.

## Disclaimer

Arbitrage betting, while legal, is frowned upon by bookmakers and may lead to limitations on your betting accounts. This tool is provided for educational purposes only, and users should use it responsibly and at their own risk.

## License

This project is licensed under the MIT License - see the LICENSE file for details.