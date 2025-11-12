import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from app.core.config import get_settings
from app.api.routes import health
from fastapi.middleware.cors import CORSMiddleware

settings = get_settings()

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(health.router, tags=["health"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
