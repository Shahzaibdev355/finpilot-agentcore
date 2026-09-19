from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.tools import BaseTool
from typing import Annotated
from typing_extensions import TypedDict

from app.services.bedrock.client import get_bedrock_runtime_client
from app.config.settings import settings
from app.mcp.client import get_mcp_tools


class MarketAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def get_market_llm():
    """
    Create the Bedrock model using FinPilot's Prompt Router.
    """
    from langchain_aws import ChatBedrockConverse

    return ChatBedrockConverse(
        model=settings.bedrock_prompt_router_arn,
        provider="amazon",
        client=get_bedrock_runtime_client(),
        temperature=0,
        max_tokens=1000,
    )


SYSTEM_PROMPT = """
You are FinPilot's Market Research Agent.

Your job is to answer questions about publicly traded companies
using the available market tools.

Available tools:

1. get_stock_quote
   Use for the latest stock price, daily change, and volume.

2. get_historical_prices
   Use for historical daily price information.

3. get_company_overview
   Use for company information and fundamental metrics such as
   sector, industry, market capitalization, P/E ratio, EPS,
   revenue, and profitability metrics.

Rules:

- Use tools when the user asks for current or company-specific data.
- Do not invent financial data.
- Clearly distinguish factual market data from your explanation.
- Do not provide personalized investment advice.
- Do not execute trades or transactions.
"""


async def create_market_agent():
    """
    Create the Market Agent using tools exposed through MCP.
    """

    # Load tools from the MCP server.
    tools: list[BaseTool] = await get_mcp_tools()

    # Create Bedrock model and bind MCP tools.
    llm = get_market_llm().bind_tools(tools)

    def call_model(state: MarketAgentState):
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            *state["messages"],
        ]

        response = llm.invoke(messages)

        return {"messages": [response]}

    tool_node = ToolNode(tools)

    graph_builder = StateGraph(MarketAgentState)

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