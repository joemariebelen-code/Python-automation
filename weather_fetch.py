# ============================================================
# weather_fetch.py
# Phase 1: Python Automation — Fetch Weather Data via API
# Save results to CSV using pandas
# ============================================================

import requests
import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# ============================================================
# CONFIGURATION — cities na kukunan ng weather data
# ============================================================
CITIES = ["Madrid", "Manila", "Barcelona", "London", "Tokyo"]
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def fetch_weather(city: str) -> dict:
    """
    Fetch current weather data for a given city.
    Returns a dictionary with weather details.
    """
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",  # Celsius
        "lang": "en"
    }

    response = requests.get(BASE_URL, params=params)

    # Check if request was successful
    if response.status_code == 200:
        data = response.json()
        return {
            "city": city,
            "temperature_c": data["main"]["temp"],
            "feels_like_c": data["main"]["feels_like"],
            "humidity_pct": data["main"]["humidity"],
            "condition": data["weather"][0]["description"],
            "wind_speed_mps": data["wind"]["speed"],
            "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    else:
        print(f"[ERROR] Failed to fetch {city}: {response.status_code}")
        return None

def save_to_csv(records: list, filename: str = "weather_data.csv"):
    """
    Save list of weather records to a CSV file using pandas.
    """
    df = pd.DataFrame(records)
    df.to_csv(filename, index=False)
    print(f"[SUCCESS] Data saved to {filename}")
    print(df.to_string(index=False))  # Print table in terminal

# ============================================================
# MAIN — Run the automation
# ============================================================
if __name__ == "__main__":
    print("[INFO] Starting weather data fetch...\n")

    results = []
    for city in CITIES:
        record = fetch_weather(city)
        if record:
            results.append(record)
            print(f"[OK] {city} — {record['temperature_c']}°C, {record['condition']}")

    if results:
        save_to_csv(results)
    else:
        print("[ERROR] No data fetched. Check your API key.")
        