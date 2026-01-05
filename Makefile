.PHONY: install run format lint

install:
	uv venv
	uv pip install -e .

run:
	uv run python -m tradagent.cli --ticker AAPL --cash 10000 --positions '{"AAPL":0.10}'

format:
	uv pip install black ruff
	uv run black src
	uv run ruff check --fix src

lint:
	uv pip install ruff
	uv run ruff check src
