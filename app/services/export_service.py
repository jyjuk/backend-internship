import logging
import csv
import json
from io import StringIO
from uuid import UUID
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.user import User
from app.repositories.company import CompanyRepository
from app.repositories.company_member import CompanyMemberRepository
from app.services.redis_service import RedisService

logger = logging.getLogger(__name__)


class ExportService:
    """Service for exporting quiz in various formats"""

    def __init__(self, session: AsyncSession):
        self.company_repo = CompanyRepository(session)
        self.member_repo = CompanyMemberRepository(session)
        self.session = session

    async def _check_owner_or_admin(self, company_id: UUID, user_id: UUID) -> None:
        """Check if user is company owner or admin"""
        company = await self.company_repo.get_by_id(company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        if company.owner_id == user_id:
            return

        member = await self.member_repo.get_by_user_and_company(user_id, company_id)
        if not member or not member.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only company owner or admin can export company data"
            )

    @staticmethod
    def _response_to_json(responses: List[Dict[str, Any]]) -> str:
        """Convert response to JSON string"""
        return json.dumps(responses, indent=2, default=str)

    @staticmethod
    def _response_to_csv(responses: List[Dict[str, Any]]) -> str:
        """Convert response to CSV string"""
        if not responses:
            return ""

        output = StringIO()
        fieldnames = [
            "user_id",
            "company_id",
            "quiz_id",
            "question_id",
            "answer_ids",
            "is_correct",
            "answered_at"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for response in responses:
            response_copy = response.copy()
            response_copy["answer_ids"] = json.dumps(response["answer_ids"])
            writer.writerow(response_copy)
        return output.getvalue()

    async def export_user_responses(
            self,
            user: User,
            format: str = "json",
            quiz_id: UUID | None = None
    ) -> tuple[str, str]:
        """Export user`s own quiz responses"""
        try:
            if quiz_id:
                responses = await RedisService.get_user_quiz_responses(user.id, quiz_id)
            else:
                responses = []
            if format == "csv":
                content = self._response_to_csv(responses)
                media_type = "text/csv"
            else:
                content = self._response_to_json(responses)
                media_type = "application/json"

            return content, media_type
        except Exception as e:
            logger.error(f"Error exporting user responses: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to export responses"
            )

    async def export_company_user_responses(
            self,
            company_id: UUID,
            target_user_id: UUID,
            requester: User,
            format: str = "json",
            quiz_id: UUID | None = None
    ) -> tuple[str, str]:
        """Export specific user`s responses in company"""
        try:
            await self._check_owner_or_admin(company_id, requester.id)
            member = await self.member_repo.get_by_user_and_company(target_user_id, company_id)
            if not member:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User is not a member of this company"
                )
            if quiz_id:
                responses = await RedisService.get_user_quiz_responses(target_user_id, quiz_id)
            else:
                responses = []
            if format == "csv":
                content = self._response_to_csv(responses)
                media_type = "text/csv"
            else:
                content = self._response_to_json(responses)
                media_type = "application/json"
            return content, media_type
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error exporting company user responses {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to export responses"
            )

    async def export_quiz_responses(
            self,
            company_id: UUID,
            quiz_id: UUID,
            requester: User,
            format: str = "json",
    ) -> tuple[str, str]:
        """Export all responses for a specific quiz"""
        try:
            await self._check_owner_or_admin(company_id, requester.id)
            members = await self.member_repo.get_all(filters={"company_id": company_id})
            all_responses = []
            for member in members:
                user_responses = await RedisService.get_user_quiz_responses(member.user_id, quiz_id)
                all_responses.extend(user_responses)
            if format == "csv":
                content = self._response_to_csv(all_responses)
                media_type = "text/csv"
            else:
                content = self._response_to_json(all_responses)
                media_type = "application/json"
            return content, media_type

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error exporting quiz responses: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to export quiz responses"
            )
