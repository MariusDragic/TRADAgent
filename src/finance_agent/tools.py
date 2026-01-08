import yfinance as yf 
import numpy as np
import pandas as pd

from langchain.tools import tool
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper

wikipedia_tool = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(
        top_k_results=3,
        doc_content_chars_max=4000,
        wiki_client=None
    )
)


@tool
def get_current_stock_price(ticker: str) -> str:
    """Get the current stock price for a given ticker symbol."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        if hist.empty:
            return f"No data found for ticker symbol: {ticker}"

        current_price = hist['Close'].iloc[-1]
        return f"The current price of {ticker} is ${current_price:.2f}"
    except Exception as e:
        return f"An error occurred while fetching the stock price: {str(e)}"
    
@tool
def compute_current_moving_average(ticker: str, window: int) -> str:
    """Compute the moving average for a given stock ticker and window size."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        if hist.empty:
            return f"No data found for ticker symbol: {ticker}"

        hist['Moving_Average'] = hist['Close'].rolling(window=window).mean()
        latest_ma = hist['Moving_Average'].iloc[-1]
        return f"The {window}-day moving average for {ticker} is ${latest_ma:.2f}"
    except Exception as e:
        return f"An error occurred while computing the moving average: {str(e)}"
    
@tool
def compute_volatility(ticker: str, period: str = "1y") -> str:
    """
    Computes the annualized historical volatility based on daily log returns.
    Period examples: 30d, 90d, 6mo, 1y
    """
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)

    if hist.empty or len(hist) < 2:
        return f"Not enough data to compute volatility for {ticker}"

    returns = returns = (hist["Close"] / hist["Close"].shift(1)).apply(np.log).dropna()
    volatility = returns.std() * np.sqrt(252)

    return (
        f"The annualized volatility of {ticker} over {period} "
        f"is approximately {volatility:.2%}"
    )

TOOLS = [
    get_current_stock_price,
    compute_current_moving_average,
    compute_volatility,
    wikipedia_tool
]

if __name__ == "__main__":
    print(get_current_stock_price.invoke({"ticker": "AAPL"}))
    print(compute_current_moving_average.invoke({"ticker": "AAPL", "window": 20}))
    print(compute_volatility.invoke({"ticker": "AAPL", "period": "1y"}))
