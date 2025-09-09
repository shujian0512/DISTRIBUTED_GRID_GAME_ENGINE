"""
This file contains the pytest fixtures for the tests.
"""
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine


from app.main import app
from app.database import get_session
from app.models import Player, Game, GamePlayer, Move

# Use an in-memory SQLite database for testing
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

@pytest.fixture(scope="session", autouse=True)
def db_setup_and_teardown():
    """
    Fixture to create and drop database tables for the test session.
    """
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def session() -> Generator[Session, None, None]:
    """
    Pytest fixture to provide a clean database session for each test function.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(session: Session) -> Generator[TestClient, None, None]:
    """
    Pytest fixture to provide a TestClient with an overridden database dependency.
    """
    def get_session_override():
        return session

    # Override the app's dependency with the test session
    app.dependency_overrides[get_session] = get_session_override
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up the dependency override after the test
    app.dependency_overrides.clear()