from __future__ import annotations

import argparse
import json
import sys

from tradagent.agent import TRADAgent
from tradagent.analytics.features import FeatureEngineer
from tradagent.config import get_settings
from tradagent.llm.mistral_client import MistralToolCaller
from tradagent.market.yahoo import YahooMarketData
from tradagent.memory.sqlite import SQLiteMemory
from tradagent.models import PortfolioState


def main() -> None:
    parser = argparse.ArgumentParser(prog="tradagent")
    parser.add_argument("--ticker", required=True, type=str)
    parser.add_argument("--cash", required=True, type=float)
    parser.add_argument("--positions", default="{}", type=str)
    args = parser.parse_args()

    try:
        positions = json.loads(args.positions)
        if not isinstance(positions, dict):
            raise ValueError("positions must be a JSON object mapping ticker->weight")
        positions = {str(k): float(v) for k, v in positions.items()}
    except Exception as exc:
        raise ValueError(f"Invalid --positions: {exc}") from exc

    settings = get_settings()

    portfolio = PortfolioState(cash=float(args.cash), positions=positions)
    print(f"\n🚀 Starting TRADAgent for {args.ticker}")
    print(f"Portfolio: ${portfolio.cash:.2f} cash, positions: {portfolio.positions}\n")

    agent = TRADAgent(
        llm=MistralToolCaller(
            api_key=settings.mistral_api_key,
            model=settings.mistral_model,
        ),
        market=YahooMarketData(),
        fe=FeatureEngineer(),
        memory=SQLiteMemory(db_path=settings.db_path),
    )

    result = agent.run(ticker=args.ticker, portfolio=portfolio)
    print("\n" + "="*60)
    print("DECISION RESULT")
    print("="*60)
    sys.stdout.write(json.dumps(result, indent=2) + "\n")

if __name__ == "__main__":
    main()