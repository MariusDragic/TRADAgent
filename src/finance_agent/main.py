from langchain.messages import HumanMessage

from .agent import build_agent
from .utils import extract_final_answer


def main():
    agent = build_agent()

    print("📈 Financial Agent (Mistral Medium)")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("🧑 > ")

        if user_input.lower() in {"exit", "quit"}:
            break

        response = agent.invoke(
            {
                "messages": [
                    HumanMessage(content=user_input)
                ]
            }
        )
        response = extract_final_answer(response)
        print("\n🤖 >", response, "\n")


if __name__ == "__main__":
    main()
