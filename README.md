# TRADAgent

A minimal trading decision agent using Mistral tool calling and Yahoo price history.

## Setup

1. Create `.env` with:
   - `MISTRAL_API_KEY=...`
   - `MISTRAL_MODEL=mistral-small-latest`

2. Install with uv:
   - `make install`

## Run

```bash
make run
# or:
uv run tradagent --ticker AAPL --cash 10000 --positions '{"AAPL":0.10}'
