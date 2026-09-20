from langchain_core.tools import tool

from app.schemas.finance.portfolio import (
    PortfolioHolding,
    PortfolioSummary,
)
from app.services.portfolio.service import PortfolioService


service = PortfolioService()


@tool
def calculate_portfolio() -> PortfolioSummary:
    """
    Calculate the current value, invested amount, profit/loss,
    return percentage, and allocation of the demo portfolio.
    """

    raw_holdings = service.get_demo_portfolio()

    holdings = []

    total_invested = 0.0
    total_value = 0.0

    for item in raw_holdings:
        invested_value = item["quantity"] * item["average_price"]

        current_value = item["quantity"] * item["current_price"]

        profit_loss = current_value - invested_value

        return_percent = (
            (profit_loss / invested_value) * 100 if invested_value > 0 else 0.0
        )

        total_invested += invested_value
        total_value += current_value

        holdings.append(
            PortfolioHolding(
                symbol=item["symbol"],
                quantity=item["quantity"],
                average_price=item["average_price"],
                current_price=item["current_price"],
                invested_value=invested_value,
                current_value=current_value,
                profit_loss=profit_loss,
                return_percent=return_percent,
                allocation_percent=0.0,
            )
        )

    total_profit_loss = total_value - total_invested

    total_return_percent = (
        (total_profit_loss / total_invested) * 100 if total_invested > 0 else 0.0
    )

    for holding in holdings:
        holding.allocation_percent = (
            (holding.current_value / total_value) * 100 if total_value > 0 else 0.0
        )

    return PortfolioSummary(
        total_invested=total_invested,
        total_value=total_value,
        total_profit_loss=total_profit_loss,
        total_return_percent=total_return_percent,
        holdings=holdings,
    )
