from pydantic import BaseModel


class CompanyOverview(BaseModel):
    symbol: str
    name: str
    description: str
    exchange: str
    currency: str
    country: str
    sector: str
    industry: str

    market_cap: int | None = None
    pe_ratio: float | None = None
    peg_ratio: float | None = None
    book_value: float | None = None
    dividend_per_share: float | None = None
    dividend_yield: float | None = None
    eps: float | None = None

    profit_margin: float | None = None
    operating_margin: float | None = None
    return_on_equity: float | None = None

    revenue_ttm: int | None = None
    gross_profit_ttm: int | None = None

    quarterly_earnings_growth_yoy: float | None = None
    quarterly_revenue_growth_yoy: float | None = None
