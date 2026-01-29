from fastapi import APIRouter
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """ Health check endpoint. Returns: Status of the application"""
    return HealthResponse(
        status_code=200,
        detail="ok",
        result="working"
    )
