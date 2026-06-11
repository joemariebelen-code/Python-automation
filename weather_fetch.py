# ============================================================
# weather_fetch.py
# Phase 1: Fetch weather data via OpenWeatherMap API -> CSV
# Phase 2: Send daily report via email (HTML table + CSV attachment)
# ============================================================

import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

import requests
import pandas as pd
from dotenv import load_dotenv

# ============================================================
# CONFIGURATION
# ============================================================
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"  # https for security

# Email config (loaded from .env)
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# Cities na kukunan ng weather data
CITIES = [
    "Madrid", "Manila", "Barcelona", "London", "Tokyo",
    "Moscow", "New York", "Sydney", "Cairo", "Rio de Janeiro",
]


# ============================================================
# FETCH WEATHER
# ============================================================
def fetch_weather(city: str) -> dict | None:
    """
    Fetch current weather data for a given city.
    Returns a dict with weather details, or None if it fails
    (network error, bad API key, city not found, etc.)
    """
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",  # Celsius
        "lang": "en",
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()  # raises error on 4xx/5xx (bad key, city not found, etc.)
        data = response.json()

        return {
            "city": city,
            "temperature_c": data["main"]["temp"],
            "feels_like_c": data["main"]["feels_like"],
            "humidity_pct": data["main"]["humidity"],
            "condition": data["weather"][0]["description"],
            "wind_speed_mps": data["wind"]["speed"],
            "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    except requests.exceptions.HTTPError as http_err:
        print(f"[ERROR] {city} -> HTTP error: {http_err}")
    except requests.exceptions.RequestException as req_err:
        # Covers timeouts, no internet, DNS failure, etc.
        print(f"[ERROR] {city} -> Network error: {req_err}")
    except (KeyError, IndexError) as parse_err:
        print(f"[ERROR] {city} -> Unexpected response format: {parse_err}")

    return None


# ============================================================
# SAVE TO CSV
# ============================================================
def save_to_csv(records: list, filename: str = "weather_data.csv") -> None:
    """Save list of weather records to a CSV file using pandas."""
    df = pd.DataFrame(records)
    df.to_csv(filename, index=False)
    print(f"[SUCCESS] Data saved to {filename}")
    print(df.to_string(index=False))


# ============================================================
# SEND EMAIL REPORT
# ============================================================
def send_email_report(records: list, csv_filename: str = "weather_data.csv") -> None:
    """
    Send the weather report via email - HTML table in the body,
    plus the CSV as an attachment.

    Requires EMAIL_SENDER, EMAIL_APP_PASSWORD, EMAIL_RECEIVER in .env.
    For Gmail: use an App Password (Google Account > Security > App Passwords),
    NOT your regular login password.
    """
    if not all([EMAIL_SENDER, EMAIL_APP_PASSWORD, EMAIL_RECEIVER]):
        print("[ERROR] Email not sent - missing EMAIL_SENDER / EMAIL_APP_PASSWORD / EMAIL_RECEIVER in .env")
        return

    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = f"Weather Report - {datetime.now().strftime('%Y-%m-%d')}"

    df = pd.DataFrame(records)
    table_html = df[["city", "temperature_c", "feels_like_c", "humidity_pct", "condition"]].to_html(
        index=False, border=1
    )

    body = f"""
    <html>
      <body>
        <h2>Daily Weather Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}</h2>
        {table_html}
        <p><i>Full CSV attached.</i></p>
      </body>
    </html>
    """
    msg.attach(MIMEText(body, "html"))

    if os.path.exists(csv_filename):
        with open(csv_filename, "rb") as f:
            attachment = MIMEApplication(f.read(), _subtype="csv")
            attachment.add_header("Content-Disposition", "attachment", filename=csv_filename)
            msg.attach(attachment)
    else:
        print(f"[WARNING] '{csv_filename}' not found - sending email without attachment.")

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # encrypt the connection
            server.login(EMAIL_SENDER, EMAIL_APP_PASSWORD)
            server.send_message(msg)
        print(f"[SUCCESS] Email sent to {EMAIL_RECEIVER}")

    except smtplib.SMTPAuthenticationError:
        print("[ERROR] Email login failed - check EMAIL_SENDER/EMAIL_APP_PASSWORD (use Gmail App Password)")
    except smtplib.SMTPException as smtp_err:
        print(f"[ERROR] Failed to send email: {smtp_err}")


# ============================================================
# MAIN - Run the automation
# ============================================================
if __name__ == "__main__":
    print("[INFO] Starting weather data fetch...\n")

    if not API_KEY:
        print("[ERROR] OPENWEATHER_API_KEY not set in .env. Exiting.")
        raise SystemExit(1)

    results = []
    for city in CITIES:
        record = fetch_weather(city)
        if record:
            results.append(record)
            print(f"[OK] {city} -> {record['temperature_c']}°C, {record['condition']}")

    if results:
        save_to_csv(results)
        send_email_report(results)
    else:
        print("[ERROR] No data fetched. Check your API key.")

