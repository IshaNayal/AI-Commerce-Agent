import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI

from .api.routes.health import router as health_router
from .config import settings
from .utils.errors import register_exception_handlers
from .utils.logging import configure_logging
from .api.routes.merchants import router as merchants_router

configure_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Application started: %s", settings.app_name)
    yield
    logger.info("Application stopped")


app = FastAPI(
    title="AI Growth & Agentic Commerce API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(merchants_router)
register_exception_handlers(app)


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {"message": "AI Growth & Agentic Commerce API"}