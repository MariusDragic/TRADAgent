from langchain.messages import AIMessage

def extract_final_answer(response):
    for msg in reversed(response["messages"]):
        if isinstance(msg, AIMessage) and msg.content:
            return msg.content
    return "No answer produced."
