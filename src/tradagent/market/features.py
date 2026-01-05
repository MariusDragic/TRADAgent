from __future__ import annotations

import numpy as np

from tradagent.models import MarketFeatures, PriceHistory


class FeatureEngineer:
    def compute(self, history: PriceHistory) -> MarketFeatures:
        close = np.asarray(history.close, dtype=float)

        if close.size < 60:
            raise ValueError("Not enough data to compute features (need >= 60 bars).")

        last_close = float(close[-1])
        returns = np.diff(np.log(close))
        daily_vol = float(np.std(returns[-60:], ddof=1))
        vol_annualized = daily_vol * float(np.sqrt(252.0))

        mom_20d = float((close[-1] / close[-21]) - 1.0)

        short_vol = float(np.std(returns[-20:], ddof=1))
        long_vol = float(np.std(returns[-120:], ddof=1)) if returns.size >= 120 else daily_vol
        vol_regime = float(short_vol / max(long_vol, 1e-12))

        return MarketFeatures(
            ticker=history.ticker,
            last_close=last_close,
            volatility_annualized=vol_annualized,
            momentum_20d=mom_20d,
            vol_regime=vol_regime,
        )
