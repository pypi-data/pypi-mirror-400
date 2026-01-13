"""
Main FastAPI Application
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from contextlib import asynccontextmanager
import logging
import os

from ameck_copilot.app.config import get_settings
from ameck_copilot.app.routes import chat_router
from ameck_copilot.app.models import HealthResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    settings = get_settings()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Using model: {settings.model_name}")
    yield
    logger.info("Shutting down application")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="A GitHub Copilot-like AI coding assistant powered by Claude Opus 4.5",
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(chat_router)
    
    # Mount static files (frontend)
    static_path = os.path.join(os.path.dirname(__file__), "..", "static")
    if os.path.exists(static_path):
        app.mount("/static", StaticFiles(directory=static_path), name="static")
    
    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Serve the main application page"""
        index_path = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return HTMLResponse(content="""
        <html>
            <head><title>Ameck Copilot</title></head>
            <body>
                <h1>Welcome to Ameck Copilot</h1>
                <p>API documentation available at <a href="/api/docs">/api/docs</a></p>
            </body>
        </html>
        """)
    
    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint"""
        return HealthResponse(
            status="healthy",
            version=settings.app_version,
            model=settings.model_name
        )
    
    @app.get("/api")
    async def api_info():
        """API information endpoint"""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "model": settings.model_name,
            "endpoints": {
                "chat": "/api/chat/",
                "code_analysis": "/api/chat/code",
                "code_generation": "/api/chat/generate",
                "code_completion": "/api/chat/complete",
                "health": "/health",
                "docs": "/api/docs"
            }
        }
    
    return app


# Create the application instance
app = create_app()
