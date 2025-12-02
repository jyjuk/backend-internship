import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.user import User
from app.models.quiz_attempt import QuizAttempt
from app.repositories.quiz import QuizRepository
from app.repositories.company import CompanyRepository
from app.repositories.quiz_attempt import QuizAttemptRepository
from app.schemas.quiz import (
    QuizSubmission,
    QuizAttemptResponse,
    UserQuizStats,
    UserCompanyStats,
    UserSystemStats
)
from app.services.redis_service import RedisService

logger = logging.getLogger(__name__)


class QuizAttemptService:
    """Service for quiz attempt management"""

    def __init__(self, session: AsyncSession):
        self.quiz_repo = QuizRepository(session)
        self.company_repo = CompanyRepository(session)
        self.attempt_repo = QuizAttemptRepository(session)
        self.session = session

    async def submit_quiz(
            self,
            company_id: UUID,
            quiz_id: UUID,
            submission: QuizSubmission,
            user: User
    ) -> QuizAttemptResponse:
        """Submit quiz answers and calculate score"""
        try:
            quiz = await self.quiz_repo.get_quiz_with_questions(quiz_id)
            if not quiz or quiz.company_id != company_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Quiz not found"
                )

            submitted_question_ids = {ans.question_id for ans in submission.answers}
            quiz_question_ids = {q.id for q in quiz.questions}

            if submitted_question_ids != quiz_question_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Must answer all questions"
                )

            correct_answers = 0
            total_questions = len(quiz.questions)

            for question in quiz.questions:
                submitted = next(
                    (ans for ans in submission.answers if ans.question_id == question.id),
                    None
                )

                if not submitted:
                    continue

                correct_answer_ids = {ans.id for ans in question.answers if ans.is_correct}
                submitted_answer_ids = set(submitted.answer_ids)

                is_correct = correct_answer_ids == submitted_answer_ids

                if is_correct:
                    correct_answers += 1

                await RedisService.store_quiz_response(
                    user_id=user.id,
                    company_id=company_id,
                    quiz_id=quiz_id,
                    question_id=question.id,
                    answer_ids=submitted.answer_ids,
                    is_correct=is_correct
                )

            attempt = QuizAttempt(
                user_id=user.id,
                quiz_id=quiz_id,
                company_id=company_id,
                score=correct_answers,
                total_questions=total_questions
            )
            attempt = await self.attempt_repo.create(attempt)

            quiz.frequency += 1
            await self.quiz_repo.update(quiz)

            logger.info(
                f"Quiz attempt recorded: user {user.id}, quiz {quiz_id}, score {correct_answers}/{total_questions}")

            return QuizAttemptResponse(
                id=attempt.id,
                user_id=attempt.user_id,
                quiz_id=attempt.quiz_id,
                company_id=attempt.company_id,
                score=attempt.score,
                total_questions=attempt.total_questions,
                correct_answers=correct_answers,
                percentage=round((correct_answers / total_questions) * 100, 2),
                completed_at=attempt.created_at
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error submitting quiz: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to submit quiz"
            )

    async def get_user_company_stats(
            self,
            company_id: UUID,
            user: User
    ) -> UserCompanyStats:
        """Get user statistics within a company"""
        try:
            company = await self.company_repo.get_by_id(company_id)
            if not company:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Company not found"
                )

            stats_data = await self.attempt_repo.get_user_company_stats(user.id, company_id)

            average_score = 0.0
            if stats_data["total_questions"] > 0:
                average_score = round(
                    (stats_data["total_correct"] / stats_data["total_questions"]) * 100,
                    2
                )

            stats = UserQuizStats(
                total_attempts=stats_data["total_attempts"],
                total_questions_answered=stats_data["total_questions"],
                total_correct_answers=stats_data["total_correct"],
                average_score=average_score,
                last_attempt_at=stats_data["last_attempt"]
            )

            return UserCompanyStats(
                company_id=company_id,
                company_name=company.name,
                stats=stats
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user company stats: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get statistics"
            )

    async def get_user_system_stats(self, user: User) -> UserSystemStats:
        """Get user statistics across all companies"""
        try:
            stats_data = await self.attempt_repo.get_user_system_stats(user.id)

            average_score = 0.0
            if stats_data["total_questions"] > 0:
                average_score = round(
                    (stats_data["total_correct"] / stats_data["total_questions"]) * 100,
                    2
                )

            stats = UserQuizStats(
                total_attempts=stats_data["total_attempts"],
                total_questions_answered=stats_data["total_questions"],
                total_correct_answers=stats_data["total_correct"],
                average_score=average_score,
                last_attempt_at=stats_data["last_attempt"]
            )

            return UserSystemStats(
                stats=stats,
                companies_participated=stats_data["companies_count"]
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user system stats: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get statistics"
            )
