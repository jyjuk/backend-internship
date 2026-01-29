import sys
from pathlib import Path
from contextlib import asynccontextmanager
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from app.core.config import get_settings
from app.api.routes import include_routers
from app.core.middleware import setup_cors
from app.core.redis import get_redis_client, close_redis_client
from app.core.logging_config import setup_logging
from app.core.scheduler import start_scheduler, shutdown_scheduler

setup_logging()
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    logger.info("Starting application")

    redis_client = await get_redis_client()
    logger.info(f"Redis connected: {await redis_client.ping()}")

    start_scheduler()
    logger.info("Scheduler started")

    yield

    logger.info("Shutting down...")
    shutdown_scheduler()
    logger.info("Scheduler shut down")
    await close_redis_client()
    logger.info("Redis connection closed")


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan
)

setup_cors(app, settings)

include_routers(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
