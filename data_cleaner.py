"""
data_cleaner.py
Cleans the raw scraped climate DataFrame from climate_scraper.py.
Extracts the "Mean daily maximum" temperature row and converts it
into a simple {month: float_celsius} dictionary for easy comparison
with current weather forecast data.
"""

import re
import pandas as pd

# Row label we want to extract (must match climate_scraper.py's CLIMATE_KEYWORD)
TARGET_ROW_KEYWORD = "Mean daily maximum"

# Month columns in order (matches Wikipedia table column order)
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Regex to extract the Celsius value (first number, possibly negative)
# Handles both regular hyphen "-15.2" and Unicode minus sign "−15.2"
CELSIUS_PATTERN = re.compile(r"^[−-]?\d+\.?\d*")


def _parse_celsius(value: str) -> float:
    """
    Extract the Celsius temperature from a string like "21.4 (70.6)"
    or "−15.2 (4.6)".

    Args:
        value: Raw cell value, e.g. "21.4 (70.6)"

    Returns:
        float: Celsius value, e.g. 21.4 or -15.2

    Raises:
        ValueError: If no numeric value could be parsed.
    """
    # Normalize Unicode minus sign (U+2212) to regular hyphen (U+002D)
    # so float() can parse it correctly
    normalized = value.replace("\u2212", "-")

    match = CELSIUS_PATTERN.match(normalized.strip())
    if not match:
        raise ValueError(f"Could not parse Celsius value from: '{value}'")

    return float(match.group())


def clean_climate_data(df: pd.DataFrame) -> dict[str, float]:
    """
    Extract the "Mean daily maximum" row from the raw climate DataFrame
    and convert it to a clean {month: celsius} dictionary.

    Args:
        df: Raw DataFrame from climate_scraper.get_madrid_climate_data()

    Returns:
        dict: {"Jan": 9.6, "Feb": 11.8, ..., "Dec": 9.6}

    Raises:
        ValueError: If the target row is not found, or values can't be parsed.
    """
    # Find the row index where the first column matches our target keyword
    first_col = df.iloc[:, 0].astype(str)
    matching_rows = df[first_col.str.contains(TARGET_ROW_KEYWORD, case=False, na=False)]

    if matching_rows.empty:
        raise ValueError(
            f"Row containing '{TARGET_ROW_KEYWORD}' not found in DataFrame."
        )

    # Take the first match (should only be one)
    row = matching_rows.iloc[0]


    # Build the clean dict: {month: celsius_value}
    # Columns are multi-level (level 0 = table title, level 1 = month name)
    # so we access by position using df.columns to find the right index
    result = {}
    for month in MONTHS:
        # Find the column where level 1 (second tuple element) matches the month
        col = next(
            (c for c in df.columns if c[1] == month),
            None
        )
        if col is None:
            raise ValueError(f"Column for month '{month}' not found.")

        raw_value = row[col]
        result[month] = _parse_celsius(str(raw_value))

    return result


# Quick manual test when running this file directly
if __name__ == "__main__":
    from climate_scraper import get_madrid_climate_data

    raw_df = get_madrid_climate_data()
    cleaned = clean_climate_data(raw_df)

    print("Cleaned monthly mean daily max temperatures (°C):")
    for month, temp in cleaned.items():
        print(f"  {month}: {temp}°C")
        