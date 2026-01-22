from langchain_mistralai import ChatMistralAI
from langchain.agents import create_agent
from langchain.messages import SystemMessage

from ..config import MISTRAL_API_KEY


SYSTEM_PROMPT = """
You are an orchestration agent for a financial AI system.

Your ONLY task is to decide which agents must be executed and in which order,
based on the user request.

AVAILABLE AGENTS:
- stock_analyst_agent : produces financial analysis text
- report_writer_agent : generates and saves a PDF report from analysis

RULES:
- Do NOT perform any financial analysis yourself.
- Do NOT generate LaTeX or reports.
- ONLY output a valid JSON object.
- No explanations, no markdown.

OUTPUT FORMAT (STRICT):
{
  "run_stock_analysis": true | false,
  "run_report_generation": true | false,
  "clean_query": "<user query without meta instructions>"
}

LOGIC:
- If the user asks for analysis only → run_stock_analysis = true
- If the user asks for a report / pdf / document → run BOTH agents
- Report generation ALWAYS requires stock analysis first
"""

def build_agent():
    llm = ChatMistralAI(
        name="mistral-small",
        api_key=MISTRAL_API_KEY,
        temperature=0.0  # important for determinism
    )

    return create_agent(
        model=llm,
        tools=[],  # orchestrator has NO tools
        system_prompt=SystemMessage(content=SYSTEM_PROMPT),
    )