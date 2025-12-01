import logging
import json
from datetime import datetime
from uuid import UUID
from typing import List, Optional, Dict, Any
from app.core.redis import get_redis_client

logger = logging.getLogger(__name__)


class RedisService:
    """Service for managing quiz response in Redis"""

    RESPONSE_TTL = 172800
    KEY_PREFIX = "quiz_response"

    @staticmethod
    def _make_key(user_id: UUID, quiz_id: UUID, question_id: UUID) -> str:
        """Generate Redis key for quiz response"""
        return f"{RedisService.KEY_PREFIX}:{user_id}:{quiz_id}:{question_id}"

    @staticmethod
    def _make_pattern(user_id: UUID, quiz_id: UUID) -> str:
        """Generate Redis key pattern for all user`s response to a quiz"""
        return f"{RedisService.KEY_PREFIX}:{user_id}:{quiz_id}:*"

    @staticmethod
    async def store_quiz_response(
            user_id: UUID,
            company_id: UUID,
            quiz_id: UUID,
            question_id: UUID,
            answer_ids: List[UUID],
            is_correct: bool
    ) -> bool:
        """Store quiz response in Redis with 48 hour TTL"""
        try:
            redis = await get_redis_client()
            key = RedisService._make_key(user_id, quiz_id, question_id)
            data = {
                "user_id": str(user_id),
                "company_id": str(company_id),
                "quiz_id": str(quiz_id),
                "question_id": str(question_id),
                "answer_ids": [str(aid) for aid in answer_ids],
                "is_correct": is_correct,
                "answered_at": datetime.utcnow().isoformat()
            }
            await redis.setex(key, RedisService.RESPONSE_TTL, json.dumps(data))

            logger.info(f"Stored quiz response in Redis: {key}")
            return True
        except Exception as e:
            logger.error(f"Error storing quiz response in Redis: {str(e)}")
            return False

    @staticmethod
    async def get_question_response(
            user_id: UUID,
            quiz_id: UUID,
            question_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get user`s response to a specific question"""
        try:
            redis = await  get_redis_client()
            key = RedisService._make_key(user_id, quiz_id, question_id)
            data = await redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error getting question response from Redis: {str(e)}")
            return None

    @staticmethod
    async def get_user_quiz_responses(user_id: UUID, quiz_id: UUID) -> List[Dict[str, Any]]:
        """Get all user`s response for a specific quiz"""
        try:
            redis = await get_redis_client()
            pattern = RedisService._make_pattern(user_id, quiz_id)
            keys = []

            async for key in redis.scan_iter(match=pattern):
                keys.append(key)
            if not keys:
                return []

            responses = []
            for key in keys:
                data = await redis.get(key)
                if data:
                    responses.append(json.loads(data))

            responses.sort(key=lambda x: x.get("answered_at", ""))
            logger.info(f"Retrieved {len(responses)} quiz responses from Redis")
            return responses

        except Exception as e:
            logger.error(f"Error getting user quiz response from Redis: {str(e)}")
            return []

    @staticmethod
    async def delete_quiz_responses(user_id: UUID, quiz_id: UUID) -> int:
        """Delete all user`s response for a quiz"""
        try:
            redis = await get_redis_client()
            pattern = RedisService._make_pattern(user_id, quiz_id)
            keys = []
            async for key in redis.scan_iter(match=pattern):
                keys.append(key)

            if not keys:
                return 0
            deleted = await redis.delete(*keys)

            logger.info(f"Delete {deleted} quiz response from Redis")
            return deleted
        except Exception as e:
            logger.error(f"Error delete quiz from Redis: {str(e)}")
            return 0
