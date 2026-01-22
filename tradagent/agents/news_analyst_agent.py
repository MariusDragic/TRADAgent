from dotenv import load_dotenv
import finnhub
from datetime import date, timedelta
from newspaper import Article
from ..config import FINNHUB_API_KEY
import requests
import pandas as pd

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=IBM&apikey=demo'
r = requests.get(url)
data = r.json()


print(data)