from langchain_core.tools import tool

from app.schemas.finance.news import (
    FinancialNews,
    NewsArticle,
)
from app.services.alpha_vantage.client import AlphaVantageClient


client = AlphaVantageClient()


@tool
async def get_financial_news(
    ticker: str | None = None,
    limit: int = 10,
) -> FinancialNews:
    """
    Get recent financial news and sentiment for a company.

    Args:
        ticker: Stock ticker symbol such as AAPL, MSFT, or TSLA.
               Leave empty to get general financial news.
        limit: Maximum number of news articles to return.
    """

    data = await client.get_financial_news(
        ticker=ticker,
        limit=limit,
    )

    feed = data.get("feed", [])

    if not feed:
        raise ValueError(
            f"No financial news found" + (f" for ticker '{ticker}'." if ticker else ".")
        )

    articles = []

    for item in feed:
        sentiment_score = item.get(
            "overall_sentiment_score",
            0,
        )

        articles.append(
            NewsArticle(
                title=item.get("title", ""),
                summary=item.get("summary", ""),
                url=item.get("url", ""),
                source=item.get("source", ""),
                published_at=item.get("time_published", ""),
                sentiment=item.get(
                    "overall_sentiment_label",
                    "Unknown",
                ),
                sentiment_score=float(sentiment_score),
            )
        )

    return FinancialNews(
        ticker=ticker.upper() if ticker else None,
        articles=articles,
    )
