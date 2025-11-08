from fastapi import APIRouter

from app.api.v1 import notes

# Create the v1 API router
# This aggregates all v1 endpoints under the /v1 prefix
router = APIRouter(prefix="/v1", tags=["v1"])

# Include all v1 routers
router.include_router(notes.router)
