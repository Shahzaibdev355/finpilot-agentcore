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


class PortfolioAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def get_portfolio_llm():
    from langchain_aws import ChatBedrockConverse

    return ChatBedrockConverse(
        model=settings.bedrock_prompt_router_arn,
        provider="amazon",
        client=get_bedrock_runtime_client(),
        temperature=0,
        max_tokens=1200,
    )


SYSTEM_PROMPT = """
You are FinPilot's Portfolio Analysis Agent.

Your job is to answer questions about the user's demo portfolio
using the available portfolio calculation tool.

Available tool:

calculate_portfolio

- Use it to retrieve the current portfolio summary.
- It provides total invested value, current portfolio value,
  profit/loss, return percentage, individual holdings,
  and portfolio allocation.

Rules:

- Use the tool whenever the user asks about their portfolio.
- Do not invent portfolio data.
- Clearly explain numerical results.
- When discussing a holding, use the data returned by the tool.
- Distinguish between factual portfolio calculations and general
  financial explanations.
- Do not provide personalized investment advice.
- Do not recommend buying or selling securities.
- Do not execute trades or financial transactions.
"""


async def create_portfolio_agent():
    # Discover tools from the MCP server
    tools: list[BaseTool] = await get_mcp_tools()

    # Portfolio Agent only gets the portfolio tool
    portfolio_tools = [tool for tool in tools if tool.name == "calculate_portfolio"]

    llm = get_portfolio_llm().bind_tools(portfolio_tools)

    def call_model(state: PortfolioAgentState):
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            *state["messages"],
        ]

        response = llm.invoke(messages)

        return {"messages": [response]}

    tool_node = ToolNode(portfolio_tools)

    graph_builder = StateGraph(PortfolioAgentState)

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
