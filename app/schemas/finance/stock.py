from pydantic import BaseModel


class StockQuote(BaseModel):
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int