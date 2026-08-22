import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.config import settings
from app.utils.errors import register_exception_handlers
from app.utils.logging import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("Application started: %s", settings.app_name)
    yield
    logger.info("Application stopped")


app = FastAPI(
    title="AI Growth & Agentic Commerce API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router)
register_exception_handlers(app)


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {"message": "AI Growth & Agentic Commerce API"}