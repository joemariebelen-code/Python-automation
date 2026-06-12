"""
compare.py
Compares current Madrid weather (from weather_fetch.py results) against
historical monthly climate averages (cached in data/madrid_climate.csv,
scraped via climate_scraper.py + save_climate_cache.py) to provide context
like "X°C above/below the historical average for this month."
"""

import csv
from datetime import datetime
from pathlib import Path

# Path to cached climate baseline (relative to project root)
CLIMATE_CSV_PATH = Path("data") / "madrid_climate.csv"


def load_climate_baseline(csv_path: Path = CLIMATE_CSV_PATH) -> dict[str, float]:
    """
    Load cached historical climate data from CSV.

    Args:
        csv_path: Path to the CSV file (default: data/madrid_climate.csv)

    Returns:
        dict: {"Jan": 11.0, "Feb": 13.2, ..., "Dec": 11.3}

    Raises:
        FileNotFoundError: If the CSV cache doesn't exist yet.
            Run save_climate_cache.py first to generate it.
    """
    if not csv_path.exists():
        raise FileNotFoundError(
            f"{csv_path} not found. Run save_climate_cache.py first "
            f"to generate the historical climate cache."
        )

    baseline = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            baseline[row["month"]] = float(row["mean_daily_max_celsius"])

    return baseline


def compare_to_baseline(
    current_temp_c: float,
    baseline: dict[str, float],
    reference_date: datetime | None = None,
) -> dict:
    """
    Compare a current temperature reading to the historical average
    for the current month.

    Args:
        current_temp_c: Current temperature in Celsius (e.g., Madrid's
            temperature_c from fetch_weather()).
        baseline: Dict from load_climate_baseline().
        reference_date: Date used to determine "current month".
            Defaults to today - override for testing with a fixed date.

    Returns:
        dict: {
            "month": "Jun",
            "current_temp_c": 28.0,
            "historical_avg_c": 30.1,
            "diff_c": -2.1,
            "message": "2.1°C below the historical average for Jun (30.1°C)."
        }

    Raises:
        KeyError: If the current month abbreviation isn't found in baseline
            (should not happen with valid 12-month CSV, but guards against
            corrupted/incomplete cache files).
    """
    reference_date = reference_date or datetime.now()
    month = reference_date.strftime("%b")  # "Jun" - matches CSV month format

    if month not in baseline:
        raise KeyError(
            f"Month '{month}' not found in baseline data. "
            f"Available months: {list(baseline.keys())}"
        )

    historical_avg = baseline[month]
    diff = round(current_temp_c - historical_avg, 1)

    if diff > 0:
        message = (
            f"{abs(diff)}°C above the historical average "
            f"for {month} ({historical_avg}°C)."
        )
    elif diff < 0:
        message = (
            f"{abs(diff)}°C below the historical average "
            f"for {month} ({historical_avg}°C)."
        )
    else:
        message = f"exactly the historical average for {month} ({historical_avg}°C)."

    return {
        "month": month,
        "current_temp_c": current_temp_c,
        "historical_avg_c": historical_avg,
        "diff_c": diff,
        "message": message,
    }


# Quick manual test when running this file directly
if __name__ == "__main__":
    from weather_fetch import fetch_weather

    baseline = load_climate_baseline()
    print("Loaded baseline:")
    for month, temp in baseline.items():
        print(f"  {month}: {temp}°C")

    # Get REAL current Madrid temperature from the API
    madrid_data = fetch_weather("Madrid")

    if madrid_data:
        result = compare_to_baseline(madrid_data["temperature_c"], baseline)
        print(f"\nReal comparison (Madrid, fetched at {madrid_data['fetched_at']}):")
        print(f"  Current temp: {result['current_temp_c']}°C")
        print(f"  Month: {result['month']}")
        print(f"  Historical avg: {result['historical_avg_c']}°C")
        print(f"  Difference: {result['diff_c']}°C")
        print(f"  Message: {result['message']}")
    else:
        print("Failed to fetch Madrid weather data.")

