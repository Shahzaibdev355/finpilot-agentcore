from typing import Annotated

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from app.config.settings import settings
from app.services.bedrock.client import get_bedrock_runtime_client
from app.mcp.client import get_mcp_tools


class NewsAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def get_news_llm():
    from langchain_aws import ChatBedrockConverse

    return ChatBedrockConverse(
        model=settings.bedrock_prompt_router_arn,
        provider="amazon",
        client=get_bedrock_runtime_client(),
        temperature=0,
        max_tokens=1500,
    )


SYSTEM_PROMPT = """
You are FinPilot's Financial News Agent.

Your job is to answer questions about recent financial news
using the available financial news tool.

Available tool:

get_financial_news

- Use it to retrieve recent financial news.
- It can retrieve news for a specific stock ticker.
- It can also retrieve general financial news when no ticker is provided.

Rules:

- Use the tool when the user asks for recent or current financial news.
- Do not invent news or sentiment.
- Summarize the retrieved articles clearly.
- Mention the source when appropriate.
- If sentiment information is available, explain it as reported sentiment,
  not as a prediction of future stock performance.
- Do not provide personalized investment advice.
- Do not execute trades or transactions.
"""


async def create_news_agent():
    # Discover financial tools from the MCP server
    tools: list[BaseTool] = await get_mcp_tools()

    # Only give the News Agent the tool it needs
    news_tools = [tool for tool in tools if tool.name == "get_financial_news"]

    llm = get_news_llm().bind_tools(news_tools)

    def call_model(state: NewsAgentState):
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            *state["messages"],
        ]

        response = llm.invoke(messages)

        return {"messages": [response]}

    tool_node = ToolNode(news_tools)

    graph_builder = StateGraph(NewsAgentState)

    graph_builder.add_node("llm", call_model)
    graph_builder.add_node("tools", tool_node)

    graph_builder.add_edge(START, "llm")

    graph_builder.add_conditional_edges(
        "llm",
        tools_condition,
        {
            "tools": "tools",
            END: END,
        },
    )

    graph_builder.add_edge("tools", "llm")

    return graph_builder.compile()
