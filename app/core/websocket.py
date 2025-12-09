from typing import Dict, Set
from uuid import UUID
from fastapi import WebSocket
import logging
import json

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections for real-time notifications"""

    def __init__(self):
        self.active_connections: Dict[UUID, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: UUID):
        """Accept WebSocket connection and register user"""
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)
        logger.info(
            f"User {user_id} connected via WebSocket. Total connections: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: UUID):
        """Remove WebSocket connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)

            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

            logger.info(f"User {user_id} disconnected from WebSocket")

    async def send_personal_notification(self, user_id: UUID, message: dict):
        """Send notification to specific user's all connections"""
        if user_id in self.active_connections:
            disconnected = set()

            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {str(e)}")
                    disconnected.add(connection)

            for connection in disconnected:
                self.active_connections[user_id].discard(connection)

    async def broadcast_to_users(self, user_ids: list[UUID], message: dict):
        """Broadcast notification to multiple users"""
        for user_id in user_ids:
            await self.send_personal_notification(user_id, message)


manager = ConnectionManager()
