from fastapi import FastAPI

from app.api.router import api_router


app = FastAPI(
    title="FinPilot API",
    version="1.0.0",
    description="REST API for FinPilot",
)

app.include_router(api_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "service": "FinPilot API",
        "status": "running",
    }