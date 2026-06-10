# Python Automation — Weather API Fetcher

A Python automation script that fetches real-time weather data 
from OpenWeatherMap API and exports it to CSV.

## What It Does
- Fetches live weather data for multiple cities
- Processes data using pandas
- Exports results to CSV automatically

## Tech Stack
- Python 3.13
- requests
- pandas
- python-dotenv

##  How To Run

1. Clone the repo
2. Create virtual environment
```bash
   py -m venv venv
   venv\Scripts\activate
```
3. Install dependencies
```bash
   pip install requests pandas python-dotenv
```
4. Add your API key in `.env`


5. Run the script
```bash
   python weather_fetch.py
```

## Sample Output
| City | Temp (°C) | Condition |
|------|-----------|-----------|
| Madrid | 24.47 | clear sky |
| Manila | 30.63 | overcast clouds |
| Barcelona | 22.80 | broken clouds |
| London | 15.99 | overcast clouds |
| Tokyo | 20.28 | overcast clouds |

## 
Joe Marie Belen — [GitHub](https://github.com/joemariebelen-code)

