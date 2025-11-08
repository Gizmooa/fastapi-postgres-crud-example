import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config.db_settings import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str = "healthy"
    message: str = "API is running"


class HealthDetailResponse(HealthResponse):
    database: str = "connected"


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Basic health check endpoint to verify API is running",
)
def health_check() -> HealthResponse:
    return HealthResponse(status="healthy", message="API is running")


@router.get(
    "/health/detailed",
    response_model=HealthDetailResponse,
    summary="Detailed health check",
    description="Detailed health check that verifies database connectivity",
)
def detailed_health_check(db: Session = Depends(get_db)) -> HealthDetailResponse:
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
        message = "API and database are running"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        message = "API is running but database connection failed"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=message,
        )

    return HealthDetailResponse(
        status="healthy",
        message=message,
        database=db_status,
    )
