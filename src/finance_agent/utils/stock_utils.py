import yfinance as yf
import numpy as np
import pandas as pd

def get_latest_ohlc(ticker: str):
    hist = yf.Ticker(ticker).history(period="1mo")
    last = hist.iloc[-1]

    return {
        "open": float(last["Open"]),
        "high": float(last["High"]),
        "low": float(last["Low"]),
        "close": float(last["Close"]),
        "volume": int(last["Volume"])
    }

def compute_rsi(ticker: str, window=14):
    hist = yf.Ticker(ticker).history(period="3mo")
    delta = hist["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    rs = gain.rolling(window).mean() / loss.rolling(window).mean()
    rsi = 100 - (100 / (1 + rs))

    return float(rsi.iloc[-1])


def compute_macd(ticker: str):
    hist = yf.Ticker(ticker).history(period="6mo")
    exp12 = hist["Close"].ewm(span=12).mean()
    exp26 = hist["Close"].ewm(span=26).mean()

    macd = exp12 - exp26
    signal = macd.ewm(span=9).mean()

    return {
        "macd": float(macd.iloc[-1]),
        "signal": float(signal.iloc[-1]),
        "histogram": float((macd - signal).iloc[-1])
    }

def compute_volatility(ticker: str):
    stock = yf.Ticker(ticker)
    hist = stock.history(period='1y')

    returns = returns = (hist["Close"] / hist["Close"].shift(1)).apply(np.log).dropna()

    return {
        "vol_30d": float(returns[-30:].std() * np.sqrt(252)),
        "vol_90d": float(returns[-90:].std() * np.sqrt(252)),
        "vol_1y": float(returns.std() * np.sqrt(252))
    }

def get_earnings_and_valuation(ticker: str):
    info = yf.Ticker(ticker).info

    return {
        "eps_trailing": info.get("trailingEps"),
        "eps_forward": info.get("forwardEps"),
        "pe_trailing": info.get("trailingPE"),
        "pe_forward": info.get("forwardPE"),
        "price_to_sales": info.get("priceToSalesTrailing12Months")
    }
