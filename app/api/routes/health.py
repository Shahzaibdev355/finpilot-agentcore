from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


class HealthResponse(BaseModel):
    status: str
    service: str


@router.get(
    "",
    response_model=HealthResponse,
    summary="Check API health",
)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="FinPilot API",
    )