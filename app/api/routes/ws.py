from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.core.websocket import manager
from app.core.dependencies import get_current_user_ws
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/notifications")
async def websocket_notifications(
        websocket: WebSocket,
        current_user: User = Depends(get_current_user_ws)
):
    """
    WebSocket endpoint for real-time notifications

    Connect: ws://localhost:8000/ws/notifications?token=<your_jwt_token>
    """
    await manager.connect(websocket, current_user.id)

    try:
        await websocket.send_json({
            "type": "connection_established",
            "message": f"Connected to notifications for user {current_user.username}"
        })

        while True:
            data = await websocket.receive_text()

            if data == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(websocket, current_user.id)
        logger.info(f"User {current_user.id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for user {current_user.id}: {str(e)}")
        manager.disconnect(websocket, current_user.id)
