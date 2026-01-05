from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Action(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class PortfolioState(BaseModel):
    cash: float = Field(ge=0.0)
    positions: dict[str, float] = Field(default_factory=dict)

    def weight_of(self, ticker: str) -> float:
        return float(self.positions.get(ticker, 0.0))


class PriceHistoryRequest(BaseModel):
    ticker: str
    period: str = "6mo"
    interval: str = "1d"


class PriceHistory(BaseModel):
    ticker: str
    timestamps: list[str]
    close: list[float]


class MarketFeatures(BaseModel):
    ticker: str
    last_close: float
    volatility_annualized: float
    momentum_20d: float
    vol_regime: float

    def to_prompt_dict(self) -> dict[str, Any]:
        return self.model_dump()


class Decision(BaseModel):
    action: Action
    target_weight: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str
    risk_notes: str
