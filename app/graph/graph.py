from langgraph.graph import END, START, StateGraph

from app.graph.state import AgentState
from app.graph.nodes import (
    retrieve_context_node,
    llm_node,
    tool_node,
    route_after_llm,
)


builder = StateGraph(AgentState)


# Nodes
builder.add_node("retrieve_context", retrieve_context_node)
builder.add_node("llm", llm_node)
builder.add_node("tools", tool_node)


# START → RAG
builder.add_edge(START, "retrieve_context")


# RAG → LLM
builder.add_edge("retrieve_context", "llm")


# LLM → Tool or END
builder.add_conditional_edges(
    "llm",
    route_after_llm,
    {
        "tool": "tools",
        "end": END,
    },
)


# Tool → LLM
builder.add_edge("tools", "llm")


graph = builder.compile()