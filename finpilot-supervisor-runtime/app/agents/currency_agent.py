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


class CurrencyAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def get_currency_llm():
    from langchain_aws import ChatBedrockConverse

    return ChatBedrockConverse(
        model=settings.bedrock_prompt_router_arn,
        provider="amazon",
        client=get_bedrock_runtime_client(),
        temperature=0,
        max_tokens=800,
    )


SYSTEM_PROMPT = """
You are FinPilot's Currency Agent.

Your job is to convert amounts between currencies using the
available currency conversion tool.

Available tool:

convert_currency

- Use it whenever the user asks for a currency conversion.
- Use three-letter currency codes such as USD, EUR, GBP, and PKR.

Rules:

- Always use the tool for exchange-rate-based conversions.
- Do not invent exchange rates.
- Clearly state the original amount, currencies, exchange rate,
  converted amount, and rate date when appropriate.
- Do not provide personalized investment advice.
- Do not execute trades or financial transactions.
"""


async def create_currency_agent():
    # Discover tools from the MCP server
    tools: list[BaseTool] = await get_mcp_tools()

    # Currency Agent only gets the currency tool
    currency_tools = [tool for tool in tools if tool.name == "convert_currency"]

    llm = get_currency_llm().bind_tools(currency_tools)

    def call_model(state: CurrencyAgentState):
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            *state["messages"],
        ]

        response = llm.invoke(messages)

        return {"messages": [response]}

    tool_node = ToolNode(currency_tools)

    graph_builder = StateGraph(CurrencyAgentState)

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
