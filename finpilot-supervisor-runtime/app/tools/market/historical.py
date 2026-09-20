from datetime import date

from langchain_core.tools import tool

from app.schemas.finance.historical import (
    HistoricalPrice,
    HistoricalPrices,
)
from app.services.alpha_vantage.client import AlphaVantageClient


client = AlphaVantageClient()


@tool
async def get_historical_prices(
    symbol: str,
    outputsize: str = "compact",
) -> HistoricalPrices:
    """
    Get historical daily stock prices for a publicly traded company.

    Args:
        symbol: Stock ticker symbol, such as AAPL, MSFT, or TSLA.
        outputsize: compact for recent data or full for the full history.
    """

    data = await client.get_historical_prices(
        symbol=symbol,
        outputsize=outputsize,
    )

    time_series = data.get("Time Series (Daily)", {})

    if not time_series:
        raise ValueError(
            f"No historical price data found for symbol '{symbol}'."
        )

    prices = []

    for price_date, values in time_series.items():
        prices.append(
            HistoricalPrice(
                date=date.fromisoformat(price_date),
                open=float(values["1. open"]),
                high=float(values["2. high"]),
                low=float(values["3. low"]),
                close=float(values["4. close"]),
                volume=int(values["5. volume"]),
            )
        )

    prices.sort(key=lambda item: item.date)

    return HistoricalPrices(
        symbol=symbol.upper(),
        prices=prices,
    )