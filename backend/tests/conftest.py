from collections.abc import Generator

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.database.dependencies import get_db
from backend.app.database.session import engine
from backend.app.main import app


def reset_commerce_tables(session: Session) -> None:
    """Clear persisted commerce rows from the shared PostgreSQL database."""
    session.execute(
        text(
            "TRUNCATE TABLE chat_messages, chat_sessions, order_items, orders, cart_items, carts, inventory, products, merchants, audit_logs "
            "RESTART IDENTITY CASCADE"
        )
    )
    session.commit()


@pytest.fixture
def db() -> Generator[Session, None, None]:
    """Provide a clean, isolated database state for each service test."""
    session = Session(bind=engine, expire_on_commit=False)
    reset_commerce_tables(session)

    try:
        yield session
    finally:
        session.rollback()
        reset_commerce_tables(session)
        session.close()


@pytest.fixture(autouse=True)
def isolate_api_database() -> Generator[None, None, None]:
    """Prevent API tests from leaving state behind in the configured database."""
    session = Session(bind=engine, expire_on_commit=False)
    reset_commerce_tables(session)

    def override_get_db() -> Session:
        return session

    app.dependency_overrides[get_db] = override_get_db

    try:
        yield
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.rollback()
        reset_commerce_tables(session)
        session.close()
