import subprocess
import json
from pathlib import Path
from langchain.tools import tool

def extract_json_from_text(text: str) -> dict:
    """
    Extract JSON from text that may contain additional content.
    Tries multiple strategies to find and parse JSON.
    """
    import re
    
    # Strategy 1: Try to parse the entire text as JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Unescape if the JSON is escaped (e.g., \" instead of ")
    try:
        unescaped = text.replace('\\"', '"').replace('\\\\', '\\')
        return json.loads(unescaped)
    except json.JSONDecodeError:
        pass
    
    # Strategy 3: Look for JSON between code blocks (```json ... ```)
    json_block_pattern = r'```(?:json)?\s*(\{.*?})\s*```'
    matches = re.findall(json_block_pattern, text, re.DOTALL)
    if matches:
        try:
            return json.loads(matches[0])
        except json.JSONDecodeError:
            pass
    
    # Strategy 4: Find the first { and last } and try to parse that
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        try:
            potential_json = text[first_brace:last_brace + 1]
            return json.loads(potential_json)
        except json.JSONDecodeError:
            pass
        
        # Strategy 4b: Try unescaping the extracted JSON
        try:
            potential_json = text[first_brace:last_brace + 1]
            unescaped = potential_json.replace('\\"', '"').replace('\\\\', '\\')
            return json.loads(unescaped)
        except json.JSONDecodeError:
            pass
    
    # If all strategies fail, raise an error
    raise json.JSONDecodeError(
        "Could not extract valid JSON from text. "
        "Please ensure the analysis returns a valid JSON dictionary.",
        text,
        0
    )


def format_market_cap(market_cap):
    """Format market cap into human readable string."""
    if isinstance(market_cap, (int, float)):
        if market_cap >= 1e12:
            return f"${market_cap/1e12:.2f}T"
        elif market_cap >= 1e9:
            return f"${market_cap/1e9:.2f}B"
        elif market_cap >= 1e6:
            return f"${market_cap/1e6:.2f}M"
        else:
            return f"${market_cap:,.0f}"
    return str(market_cap)


@tool
def generate_report_from_analysis(
    analysis_json: str,
    filename: str = None,
    output_dir: str = "./reports",
) -> dict:
    """
    Generate a professional PDF report from a stock analysis dictionary.
    
    Args:
        analysis_json: JSON string containing the complete stock analysis with keys:
                      ticker, company_name, summary, current_price, market_cap, volume,
                      volatility, momentum, valuation, conclusion
        filename: Optional base filename (default: {ticker}_report)
        output_dir: Output directory for the PDF (default: ./reports)
    
    Returns:
        dict with {success, pdf_path | error, size_kb?}
    """
    try:
        # Extract and parse the analysis JSON (handles text around JSON)
        analysis = extract_json_from_text(analysis_json)
    except json.JSONDecodeError as e:
        return {
            "success": False, 
            "error": f"Invalid JSON format: {str(e)}",
            "received_text": analysis_json[:500]  # Show first 500 chars for debugging
        }

    ticker = analysis.get("ticker", "UNKNOWN")
    company_name = analysis.get("company_name", ticker)
    summary = analysis.get("summary", "No summary available.")
    
    # Extract price data
    price_data = analysis.get("price", {})
    if isinstance(price_data, dict):
        current_price = price_data.get("close", 0.0)
    else:
        current_price = analysis.get("current_price", 0.0)
    
    market_cap = analysis.get("market_cap", "N/A")
    
    # Extract volatility
    volatility = analysis.get("volatility", {})
    vol_30d = volatility.get("vol_30d", 0.0)
    vol_90d = volatility.get("vol_90d", 0.0)
    vol_1y = volatility.get("vol_1y", 0.0)
    
    # Extract momentum
    momentum = analysis.get("momentum", {})
    rsi = momentum.get("rsi_14d", 0.0)
    
    # Determine RSI interpretation
    if rsi < 30:
        rsi_interp = "Oversold"
    elif rsi > 70:
        rsi_interp = "Overbought"
    else:
        rsi_interp = "Neutral"
    
    # Handle MACD - can be a dict or flat values
    macd_data = momentum.get("macd", {})
    if isinstance(macd_data, dict):
        macd = macd_data.get("macd", 0.0)
        signal = macd_data.get("signal", 0.0)
        histogram = macd_data.get("histogram", 0.0)
    else:
        macd = momentum.get("macd", 0.0)
        signal = momentum.get("signal", 0.0)
        histogram = momentum.get("histogram", 0.0)
    
    # Determine momentum bias
    if histogram > 0 and rsi > 50:
        momentum_bias = "bullish short-term trend"
    elif histogram < 0 and rsi < 50:
        momentum_bias = "bearish short-term trend"
    else:
        momentum_bias = "neutral trend"
    
    # Extract valuation
    valuation = analysis.get("valuation", {})
    eps_trailing = valuation.get("eps_trailing", "N/A")
    eps_forward = valuation.get("eps_forward", "N/A")
    pe_trailing = valuation.get("pe_trailing", "N/A")
    pe_forward = valuation.get("pe_forward", "N/A")
    price_to_sales = valuation.get("price_to_sales", "N/A")
    
    # Format numeric values for LaTeX
    def fmt_val(val):
        if val == "N/A" or val is None:
            return "N/A"
        if isinstance(val, (int, float)):
            return f"{val:.2f}"
        return str(val)
    
    def fmt_price(val):
        if val == "N/A" or val is None:
            return "N/A"
        if isinstance(val, (int, float)):
            return f"\\${val:.2f}"
        return str(val)
    
    # Generate conclusion dynamically
    conclusion = analysis.get("conclusion", None)
    if not conclusion:
        # Build conclusion based on data
        valuation_level = "valuation premium" if isinstance(pe_trailing, (int, float)) and pe_trailing > 25 else "fair valuation"
        momentum_desc = "negative momentum" if histogram < 0 else "positive momentum"
        
        conclusion = (
            f"{company_name} remains a structurally strong company with a dominant market position "
            f"and robust earnings outlook. However, the stock currently trades at a \\textbf{{{valuation_level}}} "
            f"and exhibits \\textbf{{{momentum_desc}}}. This profile suggests caution in the short term, "
            f"while maintaining long-term attractiveness for investors tolerant to volatility."
        )
    
    # Generate LaTeX body using f-strings (format exact de l'exemple)
    latex_body = f"""\\section*{{Company Overview}}
{summary}

\\section*{{Market Snapshot}}

\\begin{{table}}[h!]
\\centering
\\begin{{tabular}}{{l c}}
\\toprule
\\textbf{{Metric}} & \\textbf{{Value}} \\\\
\\midrule
Current Stock Price & {fmt_price(current_price)} \\\\
30-day Volatility & {vol_30d*100:.2f}\\% \\\\
90-day Volatility & {vol_90d*100:.2f}\\% \\\\
1-year Volatility & {vol_1y*100:.2f}\\% \\\\
\\bottomrule
\\end{{tabular}}
\\end{{table}}

\\section*{{Momentum Indicators}}

\\begin{{table}}[h!]
\\centering
\\begin{{tabular}}{{l c}}
\\toprule
\\textbf{{Indicator}} & \\textbf{{Value}} \\\\
\\midrule
RSI (14-day) & {rsi:.2f} ({rsi_interp}) \\\\
MACD Line & {macd:.2f} \\\\
Signal Line & {signal:.2f} \\\\
MACD Histogram & {histogram:.2f} \\\\
\\bottomrule
\\end{{tabular}}
\\end{{table}}

Momentum indicators suggest a \\textbf{{{momentum_bias}}}, with {"oversold" if rsi < 30 else "overbought" if rsi > 70 else "neutral"} conditions potentially signaling a technical {"rebound" if rsi < 30 else "correction" if rsi > 70 else "consolidation"}.

\\section*{{Valuation Metrics}}

\\begin{{table}}[h!]
\\centering
\\begin{{tabular}}{{l c}}
\\toprule
\\textbf{{Valuation Metric}} & \\textbf{{Value}} \\\\
\\midrule
Trailing EPS & {fmt_price(eps_trailing)} \\\\
Forward EPS & {fmt_price(eps_forward)} \\\\
Trailing P/E & {fmt_val(pe_trailing)} \\\\
Forward P/E & {fmt_val(pe_forward)} \\\\
Price-to-Sales & {fmt_val(price_to_sales)} \\\\
\\bottomrule
\\end{{tabular}}
\\end{{table}}

\\section*{{Conclusion}}
{conclusion}"""
    
    # Use ticker as filename if not provided
    if filename is None:
        filename = f"{ticker}_report"
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Build full LaTeX document (format exact de l'exemple)
    full_latex = f"""\\documentclass[11pt,a4paper]{{article}}

% ---------- Packages ----------
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{lmodern}}
\\usepackage{{geometry}}
\\usepackage{{amsmath}}
\\usepackage{{booktabs}}
\\usepackage{{hyperref}}
\\usepackage{{fancyhdr}}
\\usepackage{{setspace}}

% ---------- Layout ----------
\\geometry{{
    left=25mm,
    right=25mm,
    top=28mm,
    bottom=30mm
}}
\\setstretch{{1.1}}

% ---------- Header ----------
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\lhead{{\\textbf{{{ticker} — Fundamental Snapshot}}}}
\\rhead{{\\textit{{Generated by TRADAgent}}}}
\\cfoot{{\\thepage}}
\\renewcommand{{\\headrulewidth}}{{0.6pt}}

% ---------- Document ----------
\\begin{{document}}

\\vspace*{{-1cm}}
\\begin{{center}}
    {{\\LARGE \\textbf{{{company_name} ({ticker})}}}}\\\\[0.3em]
    {{\\large Fundamental Analysis Summary}}\\\\[0.6em]
    \\rule{{\\textwidth}}{{0.6pt}}
\\end{{center}}

\\vspace{{1em}}

{latex_body}

\\end{{document}}
"""
    
    # Write .tex file
    tex_file = output_path / f"{filename}.tex"
    tex_file.write_text(full_latex, encoding="utf-8")
    
    pdf_file = output_path / f"{filename}.pdf"
    
    try:
        # Compile LaTeX to PDF (run twice for proper formatting)
        last = None
        for _ in range(2):
            last = subprocess.run(
                [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    "-output-directory",
                    str(output_path),
                    str(tex_file),
                ],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',  # Replace invalid UTF-8 sequences
                timeout=60,
            )
        
        if pdf_file.exists():
            # Clean auxiliary files AND the source .tex file
            for ext in (".aux", ".log", ".out", ".toc", ".tex"):
                aux = output_path / f"{filename}{ext}"
                if aux.exists():
                    try:
                        aux.unlink()
                    except Exception:
                        pass
            
            return {
                "success": True,
                "pdf_path": str(pdf_file),
                "size_kb": round(pdf_file.stat().st_size / 1024, 2),
                "message": f"PDF compiled successfully: {pdf_file}",
            }
        
        return {
            "success": False,
            "error": "PDF file was not created",
            "log": (last.stderr if last else ""),
        }
    
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "LaTeX compilation timed out (>60s)"}
    except FileNotFoundError:
        return {
            "success": False,
            "error": "pdflatex not found. Install TeX Live (e.g., texlive-latex-base texlive-latex-extra)",
        }
    except Exception as e:
        return {"success": False, "error": f"Compilation error: {e}"}


@tool
def generate_pdf_report(
    latex_code: str,
    filename: str,
    output_dir: str = "./reports",
) -> dict:
    """
    Build a full LaTeX document from BODY-only `latex_code`, compile to PDF, and save it.

    Args:
        latex_code: The BODY of the LaTeX (no preamble, no \\begin{document}).
        filename: Base filename without extension (e.g., "AAPL_report").
        output_dir: Output directory for .tex and .pdf (default: ./reports).

    Returns:
        dict with {success, pdf_path | error, log?, size_kb?}.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    safe_title = "Financial Report"
    safe_author = "TRADAgent"

    full_latex = (
        "\\documentclass[11pt,a4paper]{article}\\n"
        "\\usepackage[utf8]{inputenc}\\n"
        "\\usepackage[T1]{fontenc}\\n"
        "\\usepackage{lmodern}\\n"
        "\\usepackage{geometry}\\n"
        "\\usepackage{amsmath}\\n"
        "\\usepackage{booktabs}\\n"
        "\\usepackage{hyperref}\\n"
        "\\usepackage{placeins}\\n"
        "\\usepackage{graphicx}\\n"
        "\\usepackage{fancyhdr}\\n"
        "\\usepackage{enumitem}\\n\\n"
        "\\geometry{left=25mm,right=25mm,top=28mm,bottom=30mm}\\n\\n"
        "\\pagestyle{fancy}\\fancyhf{}\\rhead{\\thepage}\\lhead{" + safe_title + "}\\renewcommand{\\headrulewidth}{0.4pt}\\n\\n"
        "\\title{" + safe_title + "}\\n\\author{" + safe_author + "}\\n\\date{\\today}\\n\\n"
        "\\begin{document}\\n\\n"
        "\\maketitle\\n"
        + latex_code + "\\n\\n"
        "\\end{document}\\n"
    )

    tex_file = output_path / f"{filename}.tex"
    tex_file.write_text(full_latex, encoding="utf-8")

    pdf_file = output_path / f"{filename}.pdf"

    try:
        last = None
        for _ in range(2):
            last = subprocess.run(
                [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    "-output-directory",
                    str(output_path),
                    str(tex_file),
                ],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',  # Replace invalid UTF-8 sequences
                timeout=60,
            )

        if pdf_file.exists():
            # Clean auxiliary files AND the source .tex file
            for ext in (".aux", ".log", ".out", ".toc", ".tex"):
                aux = output_path / f"{filename}{ext}"
                if aux.exists():
                    try:
                        aux.unlink()
                    except Exception:
                        pass

            return {
                "success": True,
                "pdf_path": str(pdf_file),
                "size_kb": round(pdf_file.stat().st_size / 1024, 2),
                "message": f"PDF compiled successfully: {pdf_file}",
            }

        return {
            "success": False,
            "error": "PDF file was not created",
            "log": (last.stderr if last else ""),
        }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "LaTeX compilation timed out (>60s)"}
    except FileNotFoundError:
        return {
            "success": False,
            "error": "pdflatex not found. Install TeX Live (e.g., texlive-latex-base texlive-latex-extra)",
        }
    except Exception as e:
        return {"success": False, "error": f"Compilation error: {e}"}


# Expose both tools - the new one is preferred
REPORT_TOOLS = [generate_report_from_analysis, generate_pdf_report]
