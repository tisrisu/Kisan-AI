"""
KisanAI — FastAPI Application Entry Point
Configured for local development (SQLite, demo ML mode).
"""

import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path for ML imports
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.config import settings
from app.db.database import init_db
from app.api.routes import diagnosis, feedback, history

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    logger.info(f"🌿 Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Initialize database tables
    try:
        await init_db()
        logger.info("✅ Database tables created/verified")
    except Exception as e:
        logger.warning(f"⚠️ Database initialization skipped: {e}")

    # Seed knowledge base on first run
    try:
        from app.db.seed import seed_knowledge_base
        await seed_knowledge_base()
        logger.info("✅ Knowledge base seeded")
    except Exception as e:
        logger.warning(f"⚠️ Knowledge base seeding skipped: {e}")

    # Pre-load ML service (will fall back to demo mode if no PyTorch)
    try:
        from app.services.ml_service import MLService
        ml = MLService(
            model_dir=settings.MODEL_DIR,
            knowledge_base_dir=settings.KNOWLEDGE_BASE_DIR,
        )
        logger.info("✅ ML Service initialized (demo mode if no model weights)")
    except Exception as e:
        logger.warning(f"⚠️ ML Service initialization skipped: {e}")

    logger.info(f"🚀 {settings.APP_NAME} is ready!")
    logger.info(f"📖 API docs: http://localhost:8000/docs")
    logger.info(f"🌐 Frontend: http://localhost:3000")
    yield

    # Shutdown
    logger.info(f"👋 Shutting down {settings.APP_NAME}")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered crop disease diagnosis for Indian farmers. "
                "Multi-modal fusion (Image + Text + Context) with per-district fine-tuning.",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(diagnosis.router, prefix=settings.API_PREFIX, tags=["Diagnosis"])
app.include_router(feedback.router, prefix=settings.API_PREFIX, tags=["Feedback"])
app.include_router(history.router, prefix=settings.API_PREFIX, tags=["History & Data"])


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "AI-powered crop disease diagnosis for Indian farmers",
        "docs": "/docs",
        "api_prefix": settings.API_PREFIX,
    }
