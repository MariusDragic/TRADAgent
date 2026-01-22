# TRADAgent — System for Automated Financial Analysis

TRADAgent is an automated AI-driven financial analysis system. It orchestrates specialized agents to retrieve market data, perform quantitative analysis, and generate professional PDF reports.

## Project Structure

```
TRADAgent/
├── antigrav/               # Agent memory and internal artifacts
│   ├── tests/              # Internal tests and validation scripts
│   └── CONSIGNES.md        # Permanent instructions for the agent
├── reports/                # Generated PDF reports
├── tradagent/              # Main source code
│   ├── agents/             # Agent definitions (Orchestrator, Analyst, Writer)
│   ├── tools/              # Tools for agents (YFinance, LaTeX, etc.)
│   └── utils/              # Helper utilities
├── main.py                 # Entry point of the application
├── Makefile                # Automation commands
└── pyproject.toml          # Dependencies and configuration
```

## Setup and Installation

1. **Prerequisites**:
   - Python 3.10+
   - LaTeX distribution (TeX Live) for PDF generation:
     ```bash
     sudo apt-get install texlive-latex-base texlive-latex-extra
     ```

2. **Installation**:
   ```bash
   # Create a virtual environment
   python -m venv .venv
   source .venv/bin/activate
   
   # Install dependencies
   pip install -e .
   ```

3. **Configuration**:
   - Ensure your `.env` file contains the necessary API keys (e.g., MISTRAL_API_KEY).

## Usage

Run the main application:

```bash
python main.py
```

**Commands:**
- `Analyze [TICKER]`: Performs a quantitative analysis of a stock.
- `Analyze [TICKER] and generate a report`: Analyzes and generates a PDF report.
- `exit`: Quits the application.

## Development

- All tests and experimental scripts should be placed in `antigrav/tests/` to keep the root directory clean.
- The project follows a strict "No Emoji" policy in output logs for professional use.

## License

Private Project.
