# Weather Report Automation

Automated daily weather reporting system built with Python. Fetches live weather data for 10 cities via the OpenWeatherMap API, enriches it with historical climate data scraped from Wikipedia, and delivers an HTML email report with contextual insights.

Built as part of my transition into IT/Automation — demonstrating API integration, web scraping, data cleaning, and email automation in a single production-style pipeline.

## Features

- **Multi-city weather fetch** — current conditions (temperature, humidity, wind, conditions) for 10 cities worldwide via OpenWeatherMap API
- **Historical climate baseline** — scrapes Madrid's monthly climate averages (1991–2020, AEMET data) from Wikipedia
- **Smart comparison insight** — compares current Madrid temperature against the historical average for the current month ("4.5°C below the historical average for Jun")
- **HTML email reports** — styled email with insight box, data table, and CSV attachment
- **Local caching** — climate baseline cached to CSV; no unnecessary re-scraping
- **Graceful degradation** — email still sends even if the climate cache is missing
- **Secure configuration** — all credentials managed via `.env` (never committed)

## How It Works

```
OpenWeatherMap API ──> fetch_weather() ──┐
                                          ├──> compare ──> HTML email + CSV
Wikipedia (scraped, cached) ──> baseline ─┘
```

1. `weather_fetch.py` fetches current weather for all configured cities
2. `compare.py` loads the cached climate baseline and computes the difference between Madrid's current temperature and its historical monthly average
3. An HTML email is sent with a color-coded insight box (red = hotter than average, blue = colder) and the full data table

## Project Structure

```
python-automation/
├── weather_fetch.py        # Main pipeline: fetch -> CSV -> email
├── compare.py              # Current vs historical comparison logic
├── climate_scraper.py      # Scrapes Madrid climate table from Wikipedia
├── data_cleaner.py         # Parses/cleans scraped table to {month: temp}
├── save_climate_cache.py   # One-time script: scrape + cache baseline to CSV
├── data/
│   └── madrid_climate.csv  # Cached historical baseline (mean daily max °C)
├── requirements.txt
├── .env.example            # Template for required environment variables
└── README.md
```

## Setup

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/joemariebelen-code/python-automation.git
cd python-automation
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy `.env.example` to `.env` and fill in your values:

```
OPENWEATHER_API_KEY=your_openweathermap_api_key
EMAIL_SENDER=your_email@gmail.com
EMAIL_APP_PASSWORD=your_gmail_app_password
EMAIL_RECEIVER=recipient@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

- Get a free API key at [openweathermap.org](https://openweathermap.org/api)
- For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833) (not your regular password)

### 3. Run

```bash
python weather_fetch.py
```

To refresh the historical climate baseline (e.g., once a year):

```bash
python save_climate_cache.py
```

## Technical Highlights

- **Resilient scraping** — table located by content keyword instead of hardcoded index, so the scraper survives Wikipedia layout changes; polite custom User-Agent identifying the bot
- **Real-world data cleaning** — handles multi-level pandas headers, mixed "21.4 (70.6)" C/F formats, and the Unicode minus sign (U+2212) that breaks naive `float()` parsing
- **Separation of concerns** — scraping, cleaning, caching, comparison, and reporting are independent, testable modules
- **Error handling** — network timeouts, HTTP errors, missing cache files, and SMTP failures are caught and reported without crashing the pipeline

## Roadmap

- [x] Phase 1 — API integration: multi-city fetch -> CSV -> email
- [x] Phase 2 — Web scraping: historical baseline + comparison insight
- [ ] Phase 3 — Basic ML: rain prediction model (scikit-learn)
- [ ] Phase 4 — Scheduling, logging, and monitoring
- [ ] Phase 5 — Unit tests and CI

## Author

**Joe Marie Belen** — aspiring IT/Automation professional based in Madrid
GitHub: [joemariebelen-code](https://github.com/joemariebelen-code)
