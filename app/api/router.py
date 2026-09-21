from fastapi import APIRouter

from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.api.routes.market import router as market_router
from app.api.routes.news import router as news_router
from app.api.routes.portfolio import router as portfolio_router


api_router = APIRouter(prefix="/api")

api_router.include_router(health_router)
api_router.include_router(market_router)
api_router.include_router(news_router)
api_router.include_router(portfolio_router)
api_router.include_router(chat_router)