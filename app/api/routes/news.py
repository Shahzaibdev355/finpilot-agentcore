from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.services.alpha_vantage.client import AlphaVantageClient


router = APIRouter(
    prefix="/news",
    tags=["News"],
)


class NewsArticle(BaseModel):
    title: str
    url: str
    summary: str
    source: str
    published_at: str
    sentiment_score: float | None = None
    sentiment_label: str | None = None


class NewsResponse(BaseModel):
    ticker: str | None
    articles: list[NewsArticle]


def get_alpha_vantage_client() -> AlphaVantageClient:
    return AlphaVantageClient()


@router.get(
    "",
    response_model=NewsResponse,
    summary="Get financial news",
)
async def get_financial_news(
    ticker: str | None = Query(
        default=None,
        min_length=1,
        description="Optional stock ticker symbol, e.g. AAPL",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of news articles to return",
    ),
    client: AlphaVantageClient = Depends(get_alpha_vantage_client),
) -> NewsResponse:
    result = await client.get_financial_news(
        ticker=ticker.upper() if ticker else None,
        limit=limit,
    )

    feed = result.get("feed", [])

    articles: list[NewsArticle] = []

    for item in feed:
        articles.append(
            NewsArticle(
                title=item.get("title", ""),
                url=item.get("url", ""),
                summary=item.get("summary", ""),
                source=item.get("source", ""),
                published_at=item.get("time_published", ""),
                sentiment_score=_parse_float(item.get("overall_sentiment_score")),
                sentiment_label=item.get("overall_sentiment_label"),
            )
        )

    return NewsResponse(
        ticker=ticker.upper() if ticker else None,
        articles=articles,
    )


def _parse_float(value: Any) -> float | None:
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None
