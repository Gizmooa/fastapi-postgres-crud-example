import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.config.db_settings import Base, get_db
from app.core.constants import API_VERSION_PREFIX
from app.main import app
from app.repositories.models.note import Note


# Use SQLite in-memory database for integration testing
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=test_engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_note_data() -> dict[str, str]:
    return {
        "title": "Test Note",
        "content": "This is a test note content",
    }


@pytest.fixture
def sample_note(db_session: Session, sample_note_data: dict[str, str]) -> Note:
    note = Note(
        title=sample_note_data["title"],
        content=sample_note_data["content"],
    )
    db_session.add(note)
    db_session.commit()
    db_session.refresh(note)
    return note


@pytest.fixture
def multiple_notes(db_session: Session) -> list[Note]:
    notes = [Note(title=f"Note {i}", content=f"Content {i}") for i in range(1, 6)]
    for note in notes:
        db_session.add(note)
    db_session.commit()
    for note in notes:
        db_session.refresh(note)
    return notes
