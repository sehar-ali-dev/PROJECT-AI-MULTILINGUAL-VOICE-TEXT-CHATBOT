from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.config import settings
from app.api.routes import auth
from app.api.routes import audio as audio_routes
from app.api.routes import transcription as transcription_routes
from app.db.database import engine, Base
from app.models import user, audio, transcription

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(audio_routes.router, prefix="/api/v1/audio", tags=["audio"])
app.include_router(transcription_routes.router, prefix="/api/v1/speech", tags=["speech"])


@app.on_event("startup")
async def startup_event():
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "mock_ai": settings.USE_MOCK_AI
    }


# Mount static files for frontend (must be after API routes)
frontend_path = Path(__file__).parent.parent.parent / "frontend"
app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
