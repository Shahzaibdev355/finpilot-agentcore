from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.services.alpha_vantage.client import AlphaVantageClient


router = APIRouter(
    prefix="/market",
    tags=["Market"],
)


class StockQuoteResponse(BaseModel):
    symbol: str
    price: float
    change: float
    change_percent: float


class HistoricalPrice(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class HistoricalPriceResponse(BaseModel):
    symbol: str
    data: list[HistoricalPrice]


class CompanyOverviewResponse(BaseModel):
    symbol: str
    data: dict[str, Any]


def get_alpha_vantage_client() -> AlphaVantageClient:
    return AlphaVantageClient()


@router.get(
    "/quote",
    response_model=StockQuoteResponse,
    summary="Get current stock quote",
)
async def get_stock_quote(
    symbol: str = Query(
        ...,
        min_length=1,
        description="Stock ticker symbol, e.g. AAPL",
    ),
    client: AlphaVantageClient = Depends(get_alpha_vantage_client),
) -> StockQuoteResponse:
    result = await client.get_global_quote(symbol)

    quote = result.get("Global Quote")

    if not quote:
        raise HTTPException(
            status_code=404,
            detail=f"No quote data found for symbol '{symbol.upper()}'.",
        )

    try:
        return StockQuoteResponse(
            symbol=quote["01. symbol"],
            price=float(quote["05. price"]),
            change=float(quote["09. change"]),
            change_percent=float(
                quote["10. change percent"].rstrip("%")
            ),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Invalid stock quote data received from market provider.",
        ) from exc


@router.get(
    "/history",
    response_model=HistoricalPriceResponse,
    summary="Get historical stock prices",
)
async def get_historical_prices(
    symbol: str = Query(
        ...,
        min_length=1,
        description="Stock ticker symbol, e.g. AAPL",
    ),
    client: AlphaVantageClient = Depends(get_alpha_vantage_client),
) -> HistoricalPriceResponse:
    result = await client.get_historical_prices(symbol)

    time_series = result.get("Time Series (Daily)")

    if not time_series:
        raise HTTPException(
            status_code=404,
            detail=f"No historical data found for symbol '{symbol.upper()}'.",
        )

    try:
        data = [
            HistoricalPrice(
                date=date,
                open=float(values["1. open"]),
                high=float(values["2. high"]),
                low=float(values["3. low"]),
                close=float(values["4. close"]),
                volume=int(values["5. volume"]),
            )
            for date, values in time_series.items()
        ]
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Invalid historical data received from market provider.",
        ) from exc

    return HistoricalPriceResponse(
        symbol=symbol.upper(),
        data=data,
    )


@router.get(
    "/company",
    response_model=CompanyOverviewResponse,
    summary="Get company information",
)
async def get_company_overview(
    symbol: str = Query(
        ...,
        min_length=1,
        description="Stock ticker symbol, e.g. AAPL",
    ),
    client: AlphaVantageClient = Depends(get_alpha_vantage_client),
) -> CompanyOverviewResponse:
    result = await client.get_company_overview(symbol)

    if not result or not result.get("Symbol"):
        raise HTTPException(
            status_code=404,
            detail=f"No company information found for symbol '{symbol.upper()}'.",
        )

    return CompanyOverviewResponse(
        symbol=result["Symbol"],
        data=result,
    )