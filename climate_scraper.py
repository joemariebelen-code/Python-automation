"""
climate_scraper.py
Scrapes historical climate data (monthly averages) for Madrid Barajas Airport
from Wikipedia. This data is used to compare against current/forecast weather
(from weather_fetch.py) to provide context like "X degrees above/below
historical average."
"""

import requests
import pandas as pd
from io import StringIO

# Wikipedia page containing Madrid's climate data table
WIKI_URL = "https://en.wikipedia.org/wiki/Madrid"

# Polite, transparent User-Agent - identifies the bot without exposing
# personal info, points to the public repo for context
HEADERS = {
    "User-Agent": (
        "WeatherMailBot/1.0 "
        "(+https://github.com/joemariebelen-code/python-automation)"
    )
}

# NOTE: Wikipedia uses "Mean daily maximum" wording as of 2026,
# not the older "Average high" wording. Sites change terminology over
# time, so this constant makes it easy to update in one place if it
# changes again.
CLIMATE_KEYWORD = "Mean daily maximum"


def get_madrid_climate_data() -> pd.DataFrame:
    """
    Fetch and parse the climate data table for Madrid (Barajas Airport)
    from Wikipedia.

    Returns:
        pd.DataFrame: Climate data with months as columns (multi-level
            header) and metrics (mean daily max, daily mean, precipitation,
            etc.) as rows.

    Raises:
        requests.exceptions.RequestException: If the page fetch fails.
        ValueError: If no climate table is found on the page.
    """
    response = requests.get(WIKI_URL, headers=HEADERS, timeout=10)
    response.raise_for_status()

    # pandas can read all <table> elements from raw HTML
    # StringIO wraps the HTML string so pandas doesn't complain about
    # passing raw HTML directly (deprecated behavior in newer pandas)
    tables = pd.read_html(StringIO(response.text))

    # Find the climate table by searching for a known row label.
    # We loop instead of hardcoding an index because Wikipedia page
    # structure (number/order of tables) can change over time.
    climate_table = None
    for table in tables:
        first_col = table.iloc[:, 0].astype(str)
        if first_col.str.contains(CLIMATE_KEYWORD, case=False, na=False).any():
            climate_table = table
            break  # Take the FIRST match -> Barajas Airport table

    if climate_table is None:
        raise ValueError(
            f"Could not find climate data table containing "
            f"'{CLIMATE_KEYWORD}' on the page."
        )

    return climate_table


# Quick manual test when running this file directly
if __name__ == "__main__":
    try:
        df = get_madrid_climate_data()
        print("Climate table shape:", df.shape)
        print("\nColumns:", df.columns.tolist())
        print("\nFirst column (row labels):")
        print(df.iloc[:, 0].tolist())
        print("\nFull table:")
        print(df)
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"Error scraping climate data: {e}")