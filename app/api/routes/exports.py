from fastapi import APIRouter, Depends, Query, Response
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.export_service import ExportService

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/my-responses")
async def export_my_responses(
        format: str = Query("json", regex="^(json|csv)$", description="Export format: json or csv"),
        quiz_id: UUID | None = Query(None, description="Filter by quiz ID"),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Export your own quiz responses"""
    service = ExportService(db)
    content, media_type = await service.export_user_responses(user=current_user, format=format, quiz_id=quiz_id)
    filename = f"my_quiz_responses.{format}"
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/companies/{company_id}/responses")
async def export_company_responses(
        company_id: UUID,
        format: str = Query("json", regex="^(json|csv)$", description="Export format: json or csv"),
        quiz_id: UUID | None = Query(None, description="Filter by quiz ID"),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Export all company quiz responses"""
    service = ExportService(db)
    if quiz_id:
        content, media_type = await service.export_quiz_responses(
            company_id=company_id,
            quiz_id=quiz_id,
            requester=current_user,
            format=format
        )
        filename = f"quiz_{quiz_id}_responses.{format}"
    else:
        content = "[]" if format == "json" else ""
        media_type = "application/json" if format == "json" else "text/csv"
        filename = f"company_{company_id}_responses.{format}"
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/companies/{company_id}/users/{user_id}/responses")
async def export_user_company_responses(
        company_id: UUID,
        user_id: UUID,
        format: str = Query("json", regex="^(json|csv)$", description="Export format: json or csv"),
        quiz_id: UUID | None = Query(None, description="Filter by quiz ID"),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Export specific user's quiz responses in company"""
    service = ExportService(db)
    content, media_type = await service.export_company_user_responses(
        company_id=company_id,
        target_user_id=user_id,
        requester=current_user,
        format=format,
        quiz_id=quiz_id
    )

    filename = f"user_{user_id}_responses.{format}"
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/companies/{company_id}/quizzes/{quiz_id}/responses")
async def export_quiz_responses(
        company_id: UUID,
        quiz_id: UUID,
        format: str = Query("json", regex="^(json|csv)$", description="Export format: json or csv"),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Export all responses for a specific quiz"""
    service = ExportService(db)
    content, media_type = await service.export_quiz_responses(
        company_id=company_id,
        quiz_id=quiz_id,
        requester=current_user,
        format=format
    )

    filename = f"quiz_{quiz_id}_all_responses.{format}"
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
