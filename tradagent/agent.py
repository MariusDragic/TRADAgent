from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI
from langchain.messages import SystemMessage, HumanMessage

from .config import MISTRAL_API_KEY
from .tools import TOOLS

SYSTEM_PROMPT = (
    "You are a senior financial analyst and capital markets expert. "
    "You provide rigorous, quantitative, and risk-aware analysis. "
    "When needed, you use tools to retrieve factual data such as "
    "stock prices, volatility, or company information."
)

def build_agent():
    llm = ChatMistralAI(
        name="mistral-medium", 
        api_key=MISTRAL_API_KEY,
        temperature=0.2
    )

    agent = create_agent(
        model=llm,
        tools=TOOLS,
        system_prompt=SystemMessage(content=SYSTEM_PROMPT),
    )

    return agent

