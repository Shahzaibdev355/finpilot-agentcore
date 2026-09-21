from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.agentcore.supervisor_client import SupervisorClient


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        description="User message",
    )


class ChatResponse(BaseModel):
    response: str


def get_supervisor_client() -> SupervisorClient:
    return SupervisorClient()


@router.post(
    "",
    response_model=ChatResponse,
    summary="Send a message to FinPilot Supervisor",
)
async def chat(
    request: ChatRequest,
) -> ChatResponse:
    client = get_supervisor_client()

    try:
        response = await client.invoke(
            prompt=request.message,
        )

        return ChatResponse(
            response=response,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to communicate with FinPilot Supervisor.",
        ) from exc
