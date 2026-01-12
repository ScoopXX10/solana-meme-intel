"""
FastAPI application entry point for Solana Meme Intel.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.score_router import router as score_router
from src.api.tokens_router import router as tokens_router
from src.api.watchlist_router import router as watchlist_router
from src.api.history_router import router as history_router
from src.scheduler.tasks import start_scheduler
from src.utils.logging_config import setup_logging

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup
    logger.info("Starting Solana Meme Intel backend...")
    start_scheduler()
    logger.info("Backend started successfully")

    yield

    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(
    title="Solana Meme Intel",
    version="1.0.0",
    description="Solana meme token scoring and intelligence API",
    lifespan=lifespan,
)

# CORS - allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
        "*",  # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(score_router)
app.include_router(tokens_router)
app.include_router(watchlist_router)
app.include_router(history_router)


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "message": "Solana Meme Intel backend is running!",
        "version": "1.0.0",
        "status": "healthy",
    }


@app.get("/health")
def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "scheduler": "running",
        }
    }
