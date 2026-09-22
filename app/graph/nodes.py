from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode

from app.graph.state import AgentState
from app.llm.langchain_model import LangChainGemini
from app.tools.langchain_tools import LANGCHAIN_TOOLS
from app.rag.retriever import Retriever
from app.rag.context import build_context


model = LangChainGemini()

tools_executor = ToolNode(LANGCHAIN_TOOLS)

retriever = Retriever()


def retrieve_context_node(state: AgentState) -> dict:
    task = state["task"]

    results = retriever.retrieve(
        task,
        top_k=5,
        min_score=0.0,
    )

    context = build_context(results)

    if not context:
        return {}

    return {
        "messages": [
            SystemMessage(
                content=(
                    "Repository context:\n\n"
                    + context
                )
            )
        ]
    }


def llm_node(state: AgentState) -> dict:
    response = model.invoke_with_tools(state["messages"])

    return {
        "messages": [response]
    }


def tool_node(state: AgentState) -> dict:
    return tools_executor.invoke(state)


def route_after_llm(state: AgentState) -> str:
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tool"

    return "end"