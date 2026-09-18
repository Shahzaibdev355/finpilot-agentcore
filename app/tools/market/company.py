from langchain_core.tools import tool

from app.schemas.finance.company import CompanyOverview
from app.services.alpha_vantage.client import AlphaVantageClient


client = AlphaVantageClient()


def parse_int(value: str | None) -> int | None:
    if not value or value == "None":
        return None

    return int(float(value))


def parse_float(value: str | None) -> float | None:
    if not value or value == "None":
        return None

    return float(value)


@tool
async def get_company_overview(symbol: str) -> CompanyOverview:
    """
    Get company information and fundamental financial metrics.

    Args:
        symbol: Stock ticker symbol, such as AAPL, MSFT, or TSLA.
    """

    data = await client.get_company_overview(symbol)

    if not data or not data.get("Symbol"):
        raise ValueError(f"No company overview found for symbol '{symbol}'.")

    # if not data or not data.get("Symbol"):
    #     raise ValueError(
    #         f"Alpha Vantage returned unexpected data for "
    #         f"'{symbol}': {data}"
    #     )

    return CompanyOverview(
        symbol=data["Symbol"],
        name=data.get("Name", ""),
        description=data.get("Description", ""),
        exchange=data.get("Exchange", ""),
        currency=data.get("Currency", ""),
        country=data.get("Country", ""),
        sector=data.get("Sector", ""),
        industry=data.get("Industry", ""),
        market_cap=parse_int(data.get("MarketCapitalization")),
        pe_ratio=parse_float(data.get("PERatio")),
        peg_ratio=parse_float(data.get("PEGRatio")),
        book_value=parse_float(data.get("BookValue")),
        dividend_per_share=parse_float(data.get("DividendPerShare")),
        dividend_yield=parse_float(data.get("DividendYield")),
        eps=parse_float(data.get("EPS")),
        profit_margin=parse_float(data.get("ProfitMargin")),
        operating_margin=parse_float(data.get("OperatingMarginTTM")),
        return_on_equity=parse_float(data.get("ReturnOnEquityTTM")),
        revenue_ttm=parse_int(data.get("RevenueTTM")),
        gross_profit_ttm=parse_int(data.get("GrossProfitTTM")),
        quarterly_earnings_growth_yoy=parse_float(
            data.get("QuarterlyEarningsGrowthYOY")
        ),
        quarterly_revenue_growth_yoy=parse_float(data.get("QuarterlyRevenueGrowthYOY")),
    )
