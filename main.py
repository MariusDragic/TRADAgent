import json
from langchain.messages import HumanMessage

from tradagent.agents.stock_analyst_agent import build_agent as build_stock_agent
from tradagent.agents.report_writer_agent import build_agent as build_report_agent
from tradagent.agents.orchestrator_agent import build_agent as build_orchestrator_agent
from tradagent.utils.answer_utils import extract_final_answer


def main():
    orchestrator = build_orchestrator_agent()
    stock_agent = build_stock_agent()
    report_agent = build_report_agent()

    print("=" * 60)
    print("TRADAgent -- LLM Orchestrated System")
    print("=" * 60)
    print("Examples:")
    print("  Analyze AAPL")
    print("  Analyze AAPL and generate a report")
    print("  exit")
    print("=" * 60 + "\n")

    while True:
        user_input = input("USER > ").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("\nShutting down system. Goodbye.")
            break

        if not user_input:
            continue

        # ---- Step 1: Orchestration plan ----
        orchestration_response = orchestrator.invoke({
            "messages": [HumanMessage(content=user_input)]
        })

        plan_raw = extract_final_answer(orchestration_response)

        try:
            plan = json.loads(plan_raw)
        except json.JSONDecodeError:
            print("ERROR: Orchestrator produced invalid JSON")
            # print(plan_raw) # Optional debug
            continue

        # ---- Step 2: Stock analysis (if required) ----
        analysis_json = None
        if plan["run_stock_analysis"]:
            print("\n[System] Running stock analysis agent...")
            analysis_response = stock_agent.invoke({
                "messages": [HumanMessage(content=plan["clean_query"])]
            })
            analysis_json = extract_final_answer(analysis_response)
            
            # Optional: Print preview of analysis
            # print("\n[System] Analysis completed.")

        # ---- Step 3: Report generation (if required) ----
        if plan["run_report_generation"]:
            if analysis_json:
                # Call the tool DIRECTLY instead of through the agent
                # This avoids JSON escaping issues with the LLM
                from tradagent.tools.report_writer_tools import generate_report_from_analysis
                
                print("\n[System] Generating PDF report...")
                result = generate_report_from_analysis.invoke({
                    "analysis_json": analysis_json
                })
                
                if result.get("success"):
                    print(f"[Success] Report generated successfully.")
                    print(f"Path: {result['pdf_path']}")
                    print(f"Size: {result['size_kb']} KB")
                else:
                    print(f"[Error] Report generation failed.")
                    print(f"Details: {result.get('error')}")
            else:
                print("\n[Warning] No analysis available to generate report.")

        print("\n" + "-" * 60 + "\n")


if __name__ == "__main__":
    main()
