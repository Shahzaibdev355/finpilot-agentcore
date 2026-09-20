from pydantic import BaseModel


class PortfolioHolding(BaseModel):
    symbol: str
    quantity: float
    average_price: float
    current_price: float
    invested_value: float
    current_value: float
    profit_loss: float
    return_percent: float
    allocation_percent: float


class PortfolioSummary(BaseModel):
    total_invested: float
    total_value: float
    total_profit_loss: float
    total_return_percent: float
    holdings: list[PortfolioHolding]
