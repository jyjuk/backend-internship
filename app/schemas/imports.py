from typing import List, Optional
from pydantic import BaseModel, Field


class QuizImportResult(BaseModel):
    """Result of quiz import operation"""

    created: int = Field(..., description="Number of quizzes created")
    updated: int = Field(..., description="Number of quizzes updated")
    total: int = Field(..., description="Total quizzes processed")
    errors: List[str] = Field(default_factory=list, description="List of errors encountered")

    class Config:
        json_schema_extra = {
            "example": {
                "created": 2,
                "updated": 1,
                "total": 3,
                "errors": []
            }
        }
