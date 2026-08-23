from collections.abc import Generator

import pytest
from sqlalchemy.orm import Session

from backend.app.database.dependencies import get_db
from backend.app.database.session import engine
from backend.app.main import app


@pytest.fixture
def db() -> Generator[Session, None, None]:
    """Provide a transaction-isolated session using the existing test schema."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(
        bind=connection,
        join_transaction_mode="rollback_only",
    )

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(autouse=True)
def isolate_api_database() -> Generator[None, None, None]:
    """Prevent API tests from committing rows to the configured database."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(
        bind=connection,
        join_transaction_mode="rollback_only",
    )

    def override_get_db() -> Session:
        return session

    app.dependency_overrides[get_db] = override_get_db

    try:
        yield
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        transaction.rollback()
        connection.close()
