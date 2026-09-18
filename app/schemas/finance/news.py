from pydantic import BaseModel


class NewsArticle(BaseModel):
    title: str
    summary: str
    url: str
    source: str
    published_at: str
    sentiment: str
    sentiment_score: float


class FinancialNews(BaseModel):
    ticker: str | None = None
    articles: list[NewsArticle]