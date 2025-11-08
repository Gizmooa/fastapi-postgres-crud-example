"""Root endpoint with API information."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.constants import API_VERSION, API_VERSION_PREFIX

router = APIRouter(tags=["root"])


class APIInfo(BaseModel):
    """API information response model."""

    name: str = "Notes API"
    version: str = "0.1.0"
    api_version: str = API_VERSION
    description: str = "A simple note-taking API with PostgreSQL"
    docs_url: str = "/docs"
    health_url: str = "/health"
    current_api_url: str = API_VERSION_PREFIX


@router.get(
    "/",
    response_model=APIInfo,
    summary="API Information",
    description="Get basic information about the API",
)
def root() -> APIInfo:
    """Root endpoint that returns API information.

    Returns:
        APIInfo with API name, version, and useful links
    """
    return APIInfo()
