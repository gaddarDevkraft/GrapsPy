from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
memory = ConversationBufferMemory(return_messages=True)

def create_langgraph_app():
    def classify_node(state):
        query = state["input"]
        if "search" in query.lower():
            return {"type": "search", "query": query}
        return {"type": "chat", "query": query}

    def chat_node(state):
        chain = ConversationChain(llm=llm, memory=memory)
        result = chain.run(state["query"])
        return {"response": result}

    def search_node(state):
        return {"response": f"Search results for: {state['query']}"}

    def summarizer_node(state):
        return {"final": f"Summary: {state['response']}"}

    graph = StateGraph(dict)
    graph.add_node("classify", classify_node)
    graph.add_node("chat", chat_node)
    graph.add_node("search", search_node)
    graph.add_node("summarize", summarizer_node)

    graph.set_entry_point("classify")
    graph.add_conditional_edges("classify", lambda s: s["type"])
    graph.add_edge("chat", "summarize")
    graph.add_edge("search", "summarize")
    graph.add_edge("summarize", END)

    return graph.compile()
