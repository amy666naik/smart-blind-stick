<<<<<<< HEAD
"""
FastAPI application entry point.

Wires together the database and all API routers. Run via `run.py` or
`uvicorn app.main:app --reload`.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.database.database import init_db
from app.api import device, location, events, sos
=======
"""Main FastAPI Application Entrypoint."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database.database import init_db
from app.api.emergency import router as emergency_router
from app.api.sos import router as sos_router
from app.api.device import router as device_router
from app.api.location import router as location_router
from app.api.events import router as events_router
>>>>>>> origin/feature/safety-emergency

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
<<<<<<< HEAD
=======
    """Lifespan context manager for database initialization on startup."""
>>>>>>> origin/feature/safety-emergency
    init_db()
    yield


app = FastAPI(
<<<<<<< HEAD
    title=settings.app_name,
    description=(
        "Backend foundation for the Smart Blind Stick project: device "
        "communication, GPS tracking, event ingestion, and SOS handling. "
        "Designed so the sensor-fusion, AI-vision, and safety-emergency "
        "modules can plug into the /api/events endpoint independently."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/", tags=["root"])
def root():
    return {
        "service": settings.app_name,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["root"])
def health():
    return {"status": "ok"}


app.include_router(device.router)
app.include_router(location.router)
app.include_router(events.router)
app.include_router(sos.router)
=======
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Backend foundation for the Smart Blind Stick Final-Year Project. "
        "Includes device connectivity, GPS tracking, event ingestion, and "
        "Member 3's complete Safety & Emergency subsystem (Fall Detection, Manual SOS, "
        "Confirmation Window, Guardian Notifications, and Audit Logging)."
    ),
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Subsystem Routers
app.include_router(emergency_router)
app.include_router(sos_router)
app.include_router(device_router)
app.include_router(location_router)
app.include_router(events_router)


@app.get("/", tags=["Root"])
def root():
    """Root info endpoint."""
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "subsystem": "Safety & Emergency (Member 3) + Mobile & IoT Backend",
        "docs_url": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
    }
>>>>>>> origin/feature/safety-emergency
