import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI

from .api.routes.health import router as health_router
from .api.routes.merchants import router as merchants_router
from .api.routes.products import router as products_router
from .api.routes.inventory import router as inventory_router
from .api.routes.carts import router as carts_router
from .api.routes.orders import router as orders_router
from .api.routes.chat import router as chat_router
from .config import settings
from .utils.errors import register_exception_handlers
from .utils.logging import configure_logging

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
app.include_router(products_router)
app.include_router(inventory_router)
app.include_router(carts_router)
app.include_router(orders_router)
app.include_router(chat_router)
register_exception_handlers(app)


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {"message": "AI Growth & Agentic Commerce API"}