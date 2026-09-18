from typing import Annotated

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from app.config.settings import settings
from app.services.bedrock.client import get_bedrock_runtime_client

from app.agents.market_agent import create_market_agent
from app.agents.news_agent import create_news_agent
from app.agents.currency_agent import create_currency_agent
from app.agents.portfolio_agent import create_portfolio_agent
from app.agents.financial_analysis_agent import create_financial_analysis_agent


class SupervisorState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


@tool
async def run_market_agent(question: str) -> str:
    """Use for stock prices, historical prices, company information,
    and basic market data."""

    market_agent = await create_market_agent()

    result = await market_agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question,
                }
            ]
        }
    )

    return result["messages"][-1].content


@tool
async def run_news_agent(question: str) -> str:
    """Use for recent financial news, company news,
    and financial news sentiment."""

    news_agent = await create_news_agent()

    result = await news_agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question,
                }
            ]
        }
    )

    return result["messages"][-1].content


@tool
async def run_currency_agent(question: str) -> str:
    """Use for currency conversion and exchange-rate questions."""

    currency_agent = await create_currency_agent()

    result = await currency_agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question,
                }
            ]
        }
    )

    return result["messages"][-1].content


@tool
async def run_portfolio_agent(question: str) -> str:
    """Use for demo portfolio holdings, portfolio value,
    profit/loss, returns, and allocation."""

    portfolio_agent = await create_portfolio_agent()

    result = await portfolio_agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question,
                }
            ]
        }
    )

    return result["messages"][-1].content


@tool
async def run_financial_analysis_agent(question: str) -> str:
    """Use for fundamental financial analysis and comparisons
    between publicly traded companies."""

    financial_analysis_agent = await create_financial_analysis_agent()

    result = await financial_analysis_agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question,
                }
            ]
        }
    )

    return result["messages"][-1].content


tools = [
    run_market_agent,
    run_news_agent,
    run_currency_agent,
    run_portfolio_agent,
    run_financial_analysis_agent,
]


def get_supervisor_llm():
    from langchain_aws import ChatBedrockConverse

    return ChatBedrockConverse(
        model=settings.bedrock_prompt_router_arn,
        provider="amazon",
        client=get_bedrock_runtime_client(),
        temperature=0,
        max_tokens=1200,
    )


llm = get_supervisor_llm().bind_tools(tools)


SYSTEM_PROMPT = """
You are FinPilot's Supervisor Agent.

Your job is to understand the user's request and delegate it
to the correct specialized FinPilot agent.

Available agents:

1. run_market_agent
   - Current stock prices
   - Historical stock prices
   - Company information
   - Basic market data

2. run_news_agent
   - Recent financial news
   - Company news
   - Financial news sentiment

3. run_currency_agent
   - Currency conversion
   - Exchange rates

4. run_portfolio_agent
   - Demo portfolio
   - Holdings
   - Portfolio value
   - Profit/loss
   - Returns
   - Allocation

5. run_financial_analysis_agent
   - Fundamental financial analysis
   - Company financial metrics
   - Comparing companies
   - P/E
   - Revenue
   - Profit margins
   - ROE
   - EPS

Routing rules:

- Always delegate specialized finance questions to the
  appropriate agent.
- Do not answer the specialized question yourself.
- Pass the user's complete question to the selected agent.
- Do not invent financial data.
- Do not provide personalized investment advice.
- Do not recommend buying or selling securities.
- Do not execute trades or financial transactions.
"""


def call_model(state: SupervisorState):
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        *state["messages"],
    ]

    response = llm.invoke(messages)

    return {"messages": [response]}


tool_node = ToolNode(tools)

graph_builder = StateGraph(SupervisorState)

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

supervisor_agent = graph_builder.compile()
