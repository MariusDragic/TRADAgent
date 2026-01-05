from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from tradagent.analytics.features import FeatureEngineer
from tradagent.llm.mistral_client import MistralToolCaller
from tradagent.market.yahoo import YahooMarketData
from tradagent.memory.sqlite import SQLiteMemory
from tradagent.models import PortfolioState, PriceHistoryRequest


@dataclass(frozen=True)
class TRADAgent:
    llm: MistralToolCaller
    market: YahooMarketData
    fe: FeatureEngineer
    memory: SQLiteMemory

    def run(self, ticker: str, portfolio: PortfolioState) -> dict[str, Any]:
        self.memory.init()

        system_prompt = (
            "You are TRADAgent, a trading decision agent. "
            "You must use the provided tool to fetch market data. "
            "You will receive portfolio state and computed market features. "
            "You must output a decision with action BUY, SELL, or HOLD, and a target_weight "
            "between 0 and 1. Be conservative. Prefer HOLD when uncertain. "
            "Risk constraints: never set target_weight above 0.25 for a single ticker; "
            "never increase target_weight when volatility regime is high unless momentum is strong."
        )

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_price_history",
                    "description": "Fetch historical adjusted close prices for a ticker.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticker": {"type": "string"},
                            "period": {"type": "string"},
                            "interval": {"type": "string"},
                        },
                        "required": ["ticker"],
                    },
                },
            }
        ]

        decision_schema = {
            "name": "tradagent_decision",
            "schema": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["BUY", "SELL", "HOLD"]},
                    "target_weight": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "rationale": {"type": "string"},
                    "risk_notes": {"type": "string"},
                },
                "required": [
                    "action",
                    "target_weight",
                    "confidence",
                    "rationale",
                    "risk_notes",
                ],
                "additionalProperties": False,
            },
        }

        def handle_get_price_history(args: dict[str, Any]) -> str:
            req = PriceHistoryRequest(
                ticker=str(args["ticker"]),
                period=str(args.get("period", "6mo")),
                interval=str(args.get("interval", "1d")),
            )
            history = self.market.get_price_history(req)
            features = self.fe.compute(history)
            recent = self.memory.recent_decisions(ticker=req.ticker, limit=5)

            payload = {
                "price_history": {
                    "ticker": history.ticker,
                    "timestamps": history.timestamps[-180:],
                    "close": history.close[-180:],
                },
                "features": features.to_prompt_dict(),
                "portfolio": portfolio.model_dump(),
                "current_weight": portfolio.weight_of(req.ticker),
                "recent_decisions": recent,
            }
            return json.dumps(payload)

        decision = self.llm.decide(
            system_prompt=system_prompt,
            user_payload={"ticker": ticker},
            tools=tools,
            tool_handlers={"get_price_history": handle_get_price_history},
            decision_schema=decision_schema,
        )

        capped_weight = min(float(decision.target_weight), 0.25)
        decision.target_weight = capped_weight

        self.memory.save_decision(ticker=ticker, decision=decision)

        return {"ticker": ticker, "decision": decision.model_dump()}
