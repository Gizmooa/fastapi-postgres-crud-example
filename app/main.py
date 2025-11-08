import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.config.db_settings import engine, Base
from app.config.env_settings import settings
from app.api import root, health
from app.api.v1 import router as v1_router
from app.api.exceptions import sqlalchemy_exception_handler, general_exception_handler

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    if settings.DEBUG:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created (development mode)")
    yield
    logger.info("Shutting down application...")


app: FastAPI = FastAPI(
    title="Notes API",
    description="A simple note-taking API with PostgreSQL",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "root", "description": "API information and root endpoint"},
        {"name": "v1", "description": "API version 1 endpoints"},
        {"name": "health", "description": "Health check endpoints"},
        {"name": "notes", "description": "Operations with notes (CRUD)"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(root.router)
app.include_router(health.router)
app.include_router(v1_router)
