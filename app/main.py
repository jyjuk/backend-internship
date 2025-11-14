import sys
from pathlib import Path
from contextlib import asynccontextmanager

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from app.core.config import get_settings
from app.api.routes import health
from app.core.middleware import setup_cors
from app.core.redis import get_redis_client, close_redis_client

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")

    redis_client = await get_redis_client()
    print(f"Redis connected: {await redis_client.ping()}")
    yield
    print("Shutting down...")
    await close_redis_client()
    print("Redis connection closed")


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan
)

setup_cors(app, settings)

app.include_router(health.router, tags=["health"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
