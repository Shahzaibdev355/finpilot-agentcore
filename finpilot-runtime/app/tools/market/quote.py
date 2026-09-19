from langchain_core.tools import tool

from app.schemas.finance.stock import StockQuote
from app.services.alpha_vantage.client import AlphaVantageClient


client = AlphaVantageClient()


@tool
async def get_stock_quote(symbol: str) -> StockQuote:
    """
    Get the latest stock market quote for a publicly traded company.

    Args:
        symbol: Stock ticker symbol, such as AAPL, MSFT, or TSLA.
    """
    data = await client.get_global_quote(symbol)

    quote = data.get("Global Quote", {})

    if not quote:
        raise ValueError(
            f"No stock quote data found for symbol '{symbol}'."
        )

    return StockQuote(
        symbol=quote["01. symbol"],
        price=float(quote["05. price"]),
        change=float(quote["09. change"]),
        change_percent=float(
            quote["10. change percent"].replace("%", "")
        ),
        volume=int(quote["06. volume"]),
    )