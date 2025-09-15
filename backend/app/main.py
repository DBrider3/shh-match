from contextlib import asynccontextmanager
from datetime import datetime
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import uvicorn

from app.core.config import settings
from app.core.scheduling import init_scheduler, start_scheduler, shutdown_scheduler
from app.db import schemas
from app.api.v1 import (
    routes_auth,
    routes_profile,
    routes_recs,
    routes_likes,
    routes_matches,
    routes_payments,
    routes_admin
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting SHH Match Backend API")

    # Initialize and start scheduler if not in test environment
    if settings.APP_ENV != "test":
        init_scheduler()
        start_scheduler()
        logger.info("Scheduler started")

    yield

    # Shutdown
    if settings.APP_ENV != "test":
        shutdown_scheduler()
        logger.info("Scheduler stopped")

    logger.info("SHH Match Backend API shutdown")


def create_app() -> FastAPI:
    """Create FastAPI application"""
    app = FastAPI(
        title="SHH Match Backend API",
        description="Backend API for Kakao-based matchmaking service",
        version="0.1.0",
        lifespan=lifespan
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = datetime.utcnow()

        # Log request
        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else None
        )

        response = await call_next(request)

        # Log response
        process_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            "Request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            process_time=process_time
        )

        return response

    # Exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(
            "Validation error",
            path=request.url.path,
            errors=exc.errors()
        )
        return JSONResponse(
            status_code=422,
            content={
                "error": "VALIDATION_ERROR",
                "message": "입력 데이터가 올바르지 않습니다",
                "details": exc.errors()
            }
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(request: Request, exc: SQLAlchemyError):
        logger.error(
            "Database error",
            path=request.url.path,
            error=str(exc)
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "DATABASE_ERROR",
                "message": "데이터베이스 오류가 발생했습니다"
            }
        )

    # Include routers
    app.include_router(routes_auth.router, prefix="/api/v1")
    app.include_router(routes_profile.router, prefix="/api/v1")
    app.include_router(routes_recs.router, prefix="/api/v1")
    app.include_router(routes_likes.router, prefix="/api/v1")
    app.include_router(routes_matches.router, prefix="/api/v1")
    app.include_router(routes_payments.router, prefix="/api/v1")
    app.include_router(routes_admin.router, prefix="/api/v1")

    # Health check endpoint
    @app.get("/healthz", response_model=schemas.HealthResponse)
    async def health_check():
        """Health check endpoint"""
        try:
            # Test database connection
            from app.db.session import SessionLocal
            db = SessionLocal()
            try:
                db.execute("SELECT 1")
                db_status = "healthy"
            except Exception:
                db_status = "unhealthy"
            finally:
                db.close()

            return schemas.HealthResponse(
                status="healthy" if db_status == "healthy" else "degraded",
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return schemas.HealthResponse(
                status="unhealthy",
                timestamp=datetime.utcnow()
            )

    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "SHH Match Backend API",
            "version": "0.1.0",
            "status": "running"
        }

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )