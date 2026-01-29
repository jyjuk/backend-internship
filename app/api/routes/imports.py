from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.imports import QuizImportResult
from app.services.excel_import_service import ExcelImportService

router = APIRouter()


@router.post(
    "/companies/{company_id}/quizzes/import",
    response_model=QuizImportResult,
    status_code=200,
    summary="Import quizzes from Excel file",
    description="""
    Import quizzes from Excel file. Updates existing quizzes (by title) or creates new ones.

    **Excel Format:**
    - Required columns: quiz_title, question_text, question_order, answer_text, is_correct, answer_order
    - Optional columns: quiz_description

    **Example Excel structure:**
    | quiz_title | quiz_description | question_text | question_order | answer_text | is_correct | answer_order |
    |------------|------------------|---------------|----------------|-------------|------------|--------------|
    | Python     | Learn Python     | What is it?   | 1              | Language    | TRUE       | 1            |
    | Python     | Learn Python     | What is it?   | 1              | Snake       | FALSE      | 2            |

    **Permissions:** Only company owner or admin can import quizzes.
    """,
    tags=["imports"]
)
async def import_quizzes_from_excel(
        company_id: UUID,
        file: UploadFile = File(..., description="Excel file (.xlsx or .xls)"),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Import quizzes from Excel file

    - Updates existing quizzes (matched by title)
    - Creates new quizzes if not found
    - Replaces all questions and answers for updated quizzes
    """
    service = ExcelImportService(db)

    result = await service.import_quizzes_from_excel(
        file=file,
        company_id=company_id,
        user_id=current_user.id
    )

    return result
