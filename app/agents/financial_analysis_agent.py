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


class FinancialAnalysisAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def get_financial_analysis_llm():
    from langchain_aws import ChatBedrockConverse

    return ChatBedrockConverse(
        model=settings.bedrock_prompt_router_arn,
        provider="amazon",
        client=get_bedrock_runtime_client(),
        temperature=0,
        max_tokens=1500,
    )


SYSTEM_PROMPT = """
You are FinPilot's Financial Analysis Agent.

Your job is to analyze and compare publicly traded companies
using factual financial data retrieved from the available tools.

Available tool:

get_company_overview

- Retrieves company information and fundamental financial metrics.
- Metrics include market capitalization, P/E ratio, EPS,
  revenue, profit margin, operating margin, ROE, and growth.

Use this tool whenever the user asks about company-specific
financial metrics or comparisons.

Examples:

- Compare Apple and Microsoft.
- Compare the P/E ratios of two companies.
- Which company has higher revenue?
- Compare profit margins and ROE.
- Show the fundamental metrics of Apple.

Rules:

- Do not invent financial data.
- Retrieve data using the tool before analyzing company-specific metrics.
- When comparing companies, retrieve data for each relevant company.
- Clearly identify which company each metric belongs to.
- Explain the numerical differences clearly.
- Distinguish factual financial data from your interpretation.
- Do not provide personalized investment advice.
- Do not recommend buying or selling securities.
- Do not execute trades or financial transactions.
"""


async def create_financial_analysis_agent():
    # Discover tools from the MCP server
    tools: list[BaseTool] = await get_mcp_tools()

    # Financial Analysis Agent only gets the company overview tool
    analysis_tools = [tool for tool in tools if tool.name == "get_company_overview"]

    llm = get_financial_analysis_llm().bind_tools(analysis_tools)

    def call_model(state: FinancialAnalysisAgentState):
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            *state["messages"],
        ]

        response = llm.invoke(messages)

        return {"messages": [response]}

    tool_node = ToolNode(analysis_tools)

    graph_builder = StateGraph(FinancialAnalysisAgentState)

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
