import sys
from pathlib import Path
from contextlib import asynccontextmanager
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from app.core.config import get_settings
from app.api.routes import (
    health,
    users,
    auth,
    companies,
    company_invitations,
    company_requests,
    company_members
)
from app.core.middleware import setup_cors
from app.core.redis import get_redis_client, close_redis_client
from app.core.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application")

    redis_client = await get_redis_client()
    logger.info(f"Redis connected: {await redis_client.ping()}")

    yield

    logger.info("Shutting down...")
    await close_redis_client()
    logger.info("Redis connection closed")


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan
)

setup_cors(app, settings)

app.include_router(health.router, tags=["health"])
app.include_router(users.router, tags=["users"])
app.include_router(auth.router, tags=["auth"])
app.include_router(companies.router)
app.include_router(company_invitations.router)
app.include_router(company_requests.router)
app.include_router(company_members.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
