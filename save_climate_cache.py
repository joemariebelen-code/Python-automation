"""
save_climate_cache.py
One-time (or occasional) script to scrape Madrid climate data and cache it
to a local CSV file. Run this manually when you need to refresh the
historical climate baseline (e.g., once a year, or if Wikipedia updates
their data).

This avoids hitting Wikipedia on every run of the main weather report script.
"""

import csv
from pathlib import Path

from climate_scraper import get_madrid_climate_data
from data_cleaner import clean_climate_data

# Output path - data/ folder will be created if it doesn't exist
OUTPUT_PATH = Path("data") / "madrid_climate.csv"


def save_to_csv(climate_dict: dict[str, float], output_path: Path) -> None:
    """
    Save a {month: temperature} dict to a CSV file with two columns:
    month, mean_daily_max_celsius.

    Args:
        climate_dict: Dictionary like {"Jan": 11.0, "Feb": 13.2, ...}
        output_path: Path object for the output CSV file.
    """
    # Create parent directory (data/) if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["month", "mean_daily_max_celsius"])  # header
        for month, temp in climate_dict.items():
            writer.writerow([month, temp])

    print(f"Saved {len(climate_dict)} months of data to {output_path}")


if __name__ == "__main__":
    print("Scraping Madrid climate data from Wikipedia...")
    raw_df = get_madrid_climate_data()

    print("Cleaning data...")
    cleaned = clean_climate_data(raw_df)

    print("Saving to CSV...")
    save_to_csv(cleaned, OUTPUT_PATH)

    