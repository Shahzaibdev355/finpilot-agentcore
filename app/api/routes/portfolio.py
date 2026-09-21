from fastapi import APIRouter, Depends
from app.schemas.finance.portfolio import PortfolioSummary
from app.services.portfolio.service import PortfolioService


router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"],
)


def get_portfolio_service() -> PortfolioService:
    return PortfolioService()


@router.get(
    "",
    response_model=list[dict],
    summary="Get demo portfolio holdings",
)
async def get_portfolio(
    service: PortfolioService = Depends(get_portfolio_service),
) -> list[dict]:
    return service.get_demo_portfolio()


@router.post(
    "/calculate",
    response_model=PortfolioSummary,
    summary="Calculate portfolio performance",
)
async def calculate_portfolio_endpoint(
    service: PortfolioService = Depends(get_portfolio_service),
) -> PortfolioSummary:
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
            {
                "symbol": item["symbol"],
                "quantity": item["quantity"],
                "average_price": item["average_price"],
                "current_price": item["current_price"],
                "invested_value": invested_value,
                "current_value": current_value,
                "profit_loss": profit_loss,
                "return_percent": return_percent,
                "allocation_percent": 0.0,
            }
        )

    total_profit_loss = total_value - total_invested

    total_return_percent = (
        (total_profit_loss / total_invested) * 100 if total_invested > 0 else 0.0
    )

    for holding in holdings:
        holding["allocation_percent"] = (
            (holding["current_value"] / total_value) * 100 if total_value > 0 else 0.0
        )

    return PortfolioSummary(
        total_invested=total_invested,
        total_value=total_value,
        total_profit_loss=total_profit_loss,
        total_return_percent=total_return_percent,
        holdings=holdings,
    )
