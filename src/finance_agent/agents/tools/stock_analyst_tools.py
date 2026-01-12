import yfinance as yf 
import numpy as np
import pandas as pd

from langchain.tools import tool
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper

from finance_agent.utils.stock_utils import *


wikipedia_tool = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(
        top_k_results=3,
        doc_content_chars_max=4000,
        wiki_client=None
    )
)



@tool
def get_stock_report(ticker: str) -> dict:
    """
    Returns a comprehensive stock-level quantitative report.
    """
    return {
        "price": get_latest_ohlc(ticker),
        "volatility": compute_volatility(ticker),
        "momentum": {
            "rsi_14d": compute_rsi(ticker),
            "macd": compute_macd(ticker)
        },
        "valuation": get_earnings_and_valuation(ticker)
    }

TOOLS = [
    get_stock_report,
    wikipedia_tool
]

if __name__ == "__main__":
    print(get_stock_report.invoke({"ticker": "AAPL"}))

