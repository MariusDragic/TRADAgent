from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import yfinance as yf

from tradagent.models import PriceHistory, PriceHistoryRequest


@dataclass(frozen=True)
class YahooMarketData:
    def get_price_history(self, req: PriceHistoryRequest) -> PriceHistory:
        df = yf.download(
            tickers=req.ticker,
            period=req.period,
            interval=req.interval,
            auto_adjust=True,
            progress=False,
        )

        if df is None or df.empty:
            raise ValueError(f"No data returned for ticker={req.ticker}")

        close = df["Close"]
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        timestamps = [ts.isoformat() for ts in close.index.to_pydatetime()]
        close_values = [float(x) for x in close.astype(float).tolist()]

        return PriceHistory(ticker=req.ticker, timestamps=timestamps, close=close_values)
