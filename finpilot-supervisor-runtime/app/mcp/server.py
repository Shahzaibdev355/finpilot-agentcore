import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mcp.server.fastmcp import FastMCP

from app.services.alpha_vantage.client import AlphaVantageClient
from app.tools.news.financial_news import get_financial_news
from app.tools.currency.convert import convert_currency
from app.tools.portfolio.calculator import calculate_portfolio


# mcp = FastMCP("FinPilot Finance Server")
mcp = FastMCP(
    "FinPilot Finance Server",
    host="0.0.0.0",
    stateless_http=True,
)

client = AlphaVantageClient()


# ============================================================
# MARKET TOOLS
# ============================================================


@mcp.tool()
async def get_stock_quote(symbol: str) -> dict:
    """Get the current stock quote for a given ticker symbol."""

    return await client.get_global_quote(symbol)


@mcp.tool()
async def get_historical_prices(
    symbol: str,
    outputsize: str = "compact",
) -> dict:
    """Get historical daily prices for a given ticker symbol."""

    return await client.get_historical_prices(
        symbol,
        outputsize,
    )


@mcp.tool()
async def get_company_overview(symbol: str) -> dict:
    """Get company fundamentals and overview for a given ticker symbol."""

    return await client.get_company_overview(symbol)


# ============================================================
# NEWS TOOLS
# ============================================================


@mcp.tool(name="get_financial_news")
async def get_financial_news_tool(
    ticker: str | None = None,
    limit: int = 10,
) -> dict:
    """Get recent financial news and sentiment for a company."""

    result = await get_financial_news.ainvoke(
        {
            "ticker": ticker,
            "limit": limit,
        }
    )

    return result.model_dump()


# ============================================================
# CURRENCY TOOLS
# ============================================================


@mcp.tool(name="convert_currency")
async def convert_currency_tool(
    amount: float,
    from_currency: str,
    to_currency: str,
) -> dict:
    """Convert an amount between currencies using current exchange rates."""

    result = await convert_currency.ainvoke(
        {
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
        }
    )

    return result.model_dump()


# ============================================================
# PORTFOLIO TOOLS
# ============================================================


@mcp.tool(name="calculate_portfolio")
async def calculate_portfolio_tool() -> dict:
    """Calculate the current demo portfolio summary."""

    result = await calculate_portfolio.ainvoke({})

    return result.model_dump()


# if __name__ == "__main__":
#     mcp.run()

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
