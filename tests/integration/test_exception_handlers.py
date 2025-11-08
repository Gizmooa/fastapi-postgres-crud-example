import pytest
from unittest.mock import patch
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.core.constants import API_VERSION_PREFIX
from app.main import app
from app.config.db_settings import get_db


@pytest.fixture
def exception_client(db_session: Session) -> TestClient:
    """Test client configured to not raise exceptions (for testing exception handlers)."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # raise_server_exceptions=False allows exception handlers to return responses
    test_client = TestClient(app, raise_server_exceptions=False)
    yield test_client

    app.dependency_overrides.clear()


@pytest.mark.integration
class TestSQLAlchemyExceptionHandler:
    def test_sqlalchemy_error_returns_500(self, exception_client: TestClient):
        with patch(
            "app.repositories.notes_repository.NotesRepository.create"
        ) as mock_create:
            mock_create.side_effect = SQLAlchemyError("Database connection failed")

            response = exception_client.post(
                f"{API_VERSION_PREFIX}/notes/",
                json={"title": "Test", "content": "Content"},
            )

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert (
                data["detail"] == "A database error occurred. Please try again later."
            )
            assert data["type"] == "database_error"

    def test_integrity_error_returns_500(self, exception_client: TestClient):
        with patch(
            "app.repositories.notes_repository.NotesRepository.create"
        ) as mock_create:
            mock_create.side_effect = IntegrityError("statement", "params", "orig")

            response = exception_client.post(
                f"{API_VERSION_PREFIX}/notes/",
                json={"title": "Test", "content": "Content"},
            )

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert data["type"] == "database_error"

    def test_operational_error_returns_500(self, exception_client: TestClient):
        with patch(
            "app.repositories.notes_repository.NotesRepository.get_all"
        ) as mock_get:
            mock_get.side_effect = OperationalError("statement", "params", "orig")

            response = exception_client.get(f"{API_VERSION_PREFIX}/notes/")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert data["type"] == "database_error"

    def test_sqlalchemy_error_on_get_by_id(self, exception_client: TestClient):
        with patch(
            "app.repositories.notes_repository.NotesRepository.get_by_id"
        ) as mock_get:
            mock_get.side_effect = SQLAlchemyError("Query failed")

            response = exception_client.get(f"{API_VERSION_PREFIX}/notes/1")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert data["type"] == "database_error"

    def test_sqlalchemy_error_on_update(
        self, exception_client: TestClient, sample_note
    ):
        with patch(
            "app.repositories.notes_repository.NotesRepository.update"
        ) as mock_update:
            mock_update.side_effect = SQLAlchemyError("Update failed")

            response = exception_client.put(
                f"{API_VERSION_PREFIX}/notes/{sample_note.id}",
                json={"title": "Updated", "content": "Updated content"},
            )

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert data["type"] == "database_error"

    def test_sqlalchemy_error_on_delete(
        self, exception_client: TestClient, sample_note
    ):
        with patch(
            "app.repositories.notes_repository.NotesRepository.delete"
        ) as mock_delete:
            mock_delete.side_effect = SQLAlchemyError("Delete failed")

            response = exception_client.delete(
                f"{API_VERSION_PREFIX}/notes/{sample_note.id}"
            )

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert data["type"] == "database_error"


@pytest.mark.integration
class TestGeneralExceptionHandler:
    def test_unexpected_exception_returns_500(self, exception_client: TestClient):
        with patch(
            "app.repositories.notes_repository.NotesRepository.create"
        ) as mock_create:
            mock_create.side_effect = ValueError("Unexpected error")

            response = exception_client.post(
                f"{API_VERSION_PREFIX}/notes/",
                json={"title": "Test", "content": "Content"},
            )

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert (
                data["detail"]
                == "An unexpected error occurred. Please try again later."
            )
            assert data["type"] == "internal_server_error"

    def test_key_error_returns_500(self, exception_client: TestClient):
        with patch(
            "app.repositories.notes_repository.NotesRepository.get_all"
        ) as mock_get:
            mock_get.side_effect = KeyError("missing_key")

            response = exception_client.get(f"{API_VERSION_PREFIX}/notes/")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert data["type"] == "internal_server_error"

    def test_type_error_returns_500(self, exception_client: TestClient):
        with patch(
            "app.repositories.notes_repository.NotesRepository.get_by_id"
        ) as mock_get:
            mock_get.side_effect = TypeError("Type mismatch")

            response = exception_client.get(f"{API_VERSION_PREFIX}/notes/1")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert data["type"] == "internal_server_error"

    def test_runtime_error_returns_500(self, exception_client: TestClient, sample_note):
        with patch(
            "app.repositories.notes_repository.NotesRepository.update"
        ) as mock_update:
            mock_update.side_effect = RuntimeError("Runtime issue")

            response = exception_client.patch(
                f"{API_VERSION_PREFIX}/notes/{sample_note.id}",
                json={"title": "Updated"},
            )

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert data["type"] == "internal_server_error"


@pytest.mark.integration
class TestHTTPExceptionNotCaught:
    def test_404_not_found_not_caught_by_handlers(self, client: TestClient):
        response = client.get(f"{API_VERSION_PREFIX}/notes/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "type" not in data

    def test_404_on_delete_not_caught_by_handlers(self, client: TestClient):
        response = client.delete(f"{API_VERSION_PREFIX}/notes/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "type" not in data


@pytest.mark.integration
class TestExceptionHandlerOrder:
    def test_sqlalchemy_error_takes_precedence_over_general(
        self, exception_client: TestClient
    ):
        with patch(
            "app.repositories.notes_repository.NotesRepository.create"
        ) as mock_create:
            mock_create.side_effect = SQLAlchemyError("DB error")

            response = exception_client.post(
                f"{API_VERSION_PREFIX}/notes/",
                json={"title": "Test", "content": "Content"},
            )

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert data["type"] == "database_error"
            assert "database error" in data["detail"].lower()
