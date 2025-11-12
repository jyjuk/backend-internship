from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response schema."""

    status_code: int
    detail: str
    result: str
