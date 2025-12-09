import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.user import User
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.answer import Answer
from app.repositories.company import CompanyRepository
from app.repositories.company_member import CompanyMemberRepository
from app.repositories.quiz import QuizRepository
from app.repositories.question import QuestionRepository
from app.repositories.answer import AnswerRepository
from app.schemas.quiz import (
    QuizCreate,
    QuizUpdate,
    QuizResponse,
    QuizList
)

logger = logging.getLogger(__name__)


class QuizService:
    """Service for quiz management"""

    def __init__(self, session: AsyncSession):
        self.company_repo = CompanyRepository(session)
        self.member_repo = CompanyMemberRepository(session)
        self.quiz_repo = QuizRepository(session)
        self.question_repo = QuestionRepository(session)
        self.answer_repo = AnswerRepository(session)
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
                detail="Only company owner or admin can perform this action"
            )

    async def create_quiz(self, company_id: UUID, quiz_data: QuizCreate, user: User) -> QuizResponse:
        """Create a new quiz (owner or admin only)"""
        try:
            await self._check_owner_or_admin(company_id, user.id)
            company = await self.company_repo.get_by_id(company_id)

            quiz = Quiz(
                company_id=company_id,
                title=quiz_data.title,
                description=quiz_data.description,
                frequency=0
            )
            quiz = await self.quiz_repo.create(quiz)

            for question_data in quiz_data.questions:
                question = Question(
                    quiz_id=quiz.id,
                    title=question_data.title,
                    order=question_data.order
                )
                question = await self.question_repo.create(question)

                for answer_data in question_data.answers:
                    answer = Answer(
                        question_id=question.id,
                        text=answer_data.text,
                        is_correct=answer_data.is_correct,
                        order=answer_data.order
                    )
                    await self.answer_repo.create(answer)

            try:
                from app.services.notification_service import NotificationService
                notification_service = NotificationService(self.session)

                notified_count = await notification_service.notify_quiz_created(
                    quiz_id=quiz.id,
                    quiz_title=quiz.title,
                    company_id=company_id,
                    company_name=company.name,
                    creator_id=user.id
                )

                logger.info(f"Sent {notified_count} notifications for quiz {quiz.id}")
            except Exception as e:
                logger.error(f"Failed to send notifications for quiz {quiz.id}: {str(e)}")

            complete_quiz = await self.quiz_repo.get_quiz_with_questions(quiz.id)
            logger.info(f"Quiz created: {quiz.id} in company {company_id}")
            return QuizResponse.model_validate(complete_quiz)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating quiz: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create quiz"
            )

    async def update_quiz(
            self,
            company_id: UUID,
            quiz_id: UUID,
            quiz_data: QuizUpdate,
            user: User
    ) -> QuizResponse:
        """Update quiz (owner or admin only)"""
        try:
            await self._check_owner_or_admin(company_id, user.id)

            quiz = await self.quiz_repo.get_by_id(quiz_id)
            if not quiz or quiz.company_id != company_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Quiz not found"
                )

            if quiz_data.title is not None:
                quiz.title = quiz_data.title
            if quiz_data.description is not None:
                quiz.description = quiz_data.description

            if quiz_data.questions is not None:
                for question in quiz.questions:
                    await self.question_repo.delete(question)

                for question_data in quiz_data.questions:
                    question = Question(
                        quiz_id=quiz.id,
                        title=question_data.title,
                        order=question_data.order
                    )
                    question = await self.question_repo.create(question)

                    for answer_data in question_data.answers:
                        answer = Answer(
                            question_id=question.id,
                            text=answer_data.text,
                            is_correct=answer_data.is_correct,
                            order=answer_data.order
                        )
                        await self.answer_repo.create(answer)

            quiz = await self.quiz_repo.update(quiz)
            complete_quiz = await self.quiz_repo.get_quiz_with_questions(quiz.id)
            logger.info(f"Quiz updated: {quiz_id}")
            return QuizResponse.model_validate(complete_quiz)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating quiz: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update quiz"
            )

    async def delete_quiz(self, company_id: UUID, quiz_id: UUID, user: User) -> None:
        """Delete quiz (owner or admin only)"""
        try:
            await self._check_owner_or_admin(company_id, user.id)

            quiz = await self.quiz_repo.get_by_id(quiz_id)
            if not quiz or quiz.company_id != company_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Quiz not found"
                )

            await self.quiz_repo.delete(quiz)
            logger.info(f"Quiz deleted: {quiz_id}")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting quiz: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete quiz"
            )

    async def get_company_quizzes(
            self,
            company_id: UUID,
            skip: int = 0,
            limit: int = 100
    ) -> QuizList:
        """Get all quizzes for a company (public)"""
        try:
            company = await self.company_repo.get_by_id(company_id)
            if not company:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Company not found"
                )

            quizzes = await self.quiz_repo.get_company_quizzes(company_id, skip, limit)
            total = await self.quiz_repo.count_company_quizzes(company_id)

            complete_quizzes = []
            for quiz in quizzes:
                complete_quiz = await self.quiz_repo.get_quiz_with_questions(quiz.id)
                complete_quizzes.append(QuizResponse.model_validate(complete_quiz))

            return QuizList(quizzes=complete_quizzes, total=total)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting company quizzes: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get quizzes"
            )

    async def get_quiz(self, company_id: UUID, quiz_id: UUID) -> QuizResponse:
        """Get quiz details (public)"""
        try:
            quiz = await self.quiz_repo.get_quiz_with_questions(quiz_id)
            if not quiz or quiz.company_id != company_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Quiz not found"
                )

            return QuizResponse.model_validate(quiz)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting quiz: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get quiz"
            )
