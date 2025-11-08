from datetime import datetime
from unittest.mock import Mock, patch
import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.repositories.notes_repository import NotesRepository
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse
from app.repositories.models.note import Note


@pytest.mark.unit
class TestNotesRepositoryCreate:
    def test_create_note_success(self):
        # Arrange
        mock_db = Mock()
        now = datetime.now()
        mock_note = Note(
            id=1,
            title="Test Note",
            content="Test Content",
            created_at=now,
            updated_at=now,
        )
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()

        repo = NotesRepository(mock_db)
        note_data = NoteCreate(title="Test Note", content="Test Content")

        # Act
        with patch("app.repositories.notes_repository.Note", return_value=mock_note):
            result = repo.create(note_data)

        # Assert
        assert isinstance(result, NoteResponse)
        assert result.title == "Test Note"
        assert result.content == "Test Content"
        assert result.id == 1
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_create_note_database_error(self):
        # Arrange
        mock_db = Mock()
        mock_db.add = Mock()
        mock_db.commit = Mock(side_effect=SQLAlchemyError("DB Error"))
        mock_db.rollback = Mock()

        repo = NotesRepository(mock_db)
        note_data = NoteCreate(title="Test", content="Content")

        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            repo.create(note_data)

        mock_db.rollback.assert_called_once()


@pytest.mark.unit
class TestNotesRepositoryGetAll:
    def test_get_all_empty(self):
        # Arrange
        mock_db = Mock()
        mock_scalars = Mock()
        mock_scalars.all.return_value = []
        mock_db.scalars.return_value = mock_scalars

        repo = NotesRepository(mock_db)

        # Act
        result = repo.get_all()

        # Assert
        assert result == []
        mock_db.scalars.assert_called_once()

    def test_get_all_with_pagination(self):
        # Arrange
        mock_db = Mock()
        mock_scalars = Mock()
        now = datetime.now()
        mock_notes = [
            Note(
                id=1,
                title="Note 1",
                content="Content 1",
                created_at=now,
                updated_at=now,
            ),
            Note(
                id=2,
                title="Note 2",
                content="Content 2",
                created_at=now,
                updated_at=now,
            ),
        ]
        mock_scalars.all.return_value = mock_notes
        mock_db.scalars.return_value = mock_scalars

        repo = NotesRepository(mock_db)

        # Act
        result = repo.get_all(skip=1, limit=2)

        # Assert
        assert len(result) == 2
        assert all(isinstance(note, NoteResponse) for note in result)
        mock_db.scalars.assert_called_once()

    def test_get_all_database_error(self):
        # Arrange
        mock_db = Mock()
        mock_db.scalars.side_effect = SQLAlchemyError("DB Error")

        repo = NotesRepository(mock_db)

        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            repo.get_all()


@pytest.mark.unit
class TestNotesRepositoryGetById:
    def test_get_by_id_success(self):
        # Arrange
        mock_db = Mock()
        now = datetime.now()
        mock_note = Note(
            id=1, title="Test", content="Content", created_at=now, updated_at=now
        )
        mock_db.scalar.return_value = mock_note

        repo = NotesRepository(mock_db)

        # Act
        result = repo.get_by_id(1)

        # Assert
        assert result is not None
        assert isinstance(result, NoteResponse)
        assert result.id == 1
        assert result.title == "Test"
        mock_db.scalar.assert_called_once()

    def test_get_by_id_not_found(self):
        # Arrange
        mock_db = Mock()
        mock_db.scalar.return_value = None

        repo = NotesRepository(mock_db)

        # Act
        result = repo.get_by_id(999)

        # Assert
        assert result is None


@pytest.mark.unit
class TestNotesRepositoryUpdate:
    def test_update_note_success(self):
        # Arrange
        mock_db = Mock()
        now = datetime.now()
        mock_note = Note(
            id=1,
            title="Original",
            content="Original Content",
            created_at=now,
            updated_at=now,
        )
        mock_db.scalar.return_value = mock_note

        repo = NotesRepository(mock_db)
        update_data = NoteUpdate(title="Updated", content="Updated Content")

        # Act
        result = repo.update(1, update_data)

        # Assert
        assert result is not None
        assert isinstance(result, NoteResponse)
        assert result.title == "Updated"
        assert result.content == "Updated Content"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_update_note_partial(self):
        # Arrange
        mock_db = Mock()
        now = datetime.now()
        mock_note = Note(
            id=1,
            title="Original",
            content="Original Content",
            created_at=now,
            updated_at=now,
        )
        mock_db.scalar.return_value = mock_note

        repo = NotesRepository(mock_db)
        update_data = NoteUpdate(title="Updated")

        # Act
        result = repo.update(1, update_data)

        # Assert
        assert result is not None
        assert isinstance(result, NoteResponse)
        assert result.title == "Updated"
        assert result.content == "Original Content"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_update_note_not_found(self):
        # Arrange
        mock_db = Mock()
        mock_db.scalar.return_value = None

        repo = NotesRepository(mock_db)
        update_data = NoteUpdate(title="Updated")

        # Act
        result = repo.update(999, update_data)

        # Assert
        assert result is None
        mock_db.commit.assert_not_called()


@pytest.mark.unit
class TestNotesRepositoryDelete:
    def test_delete_note_success(self):
        # Arrange
        mock_db = Mock()
        now = datetime.now()
        mock_note = Note(
            id=1, title="Test", content="Content", created_at=now, updated_at=now
        )
        mock_db.scalar.return_value = mock_note

        repo = NotesRepository(mock_db)

        # Act
        result = repo.delete(1)

        # Assert
        assert result is True
        mock_db.delete.assert_called_once_with(mock_note)
        mock_db.commit.assert_called_once()

    def test_delete_note_not_found(self):
        # Arrange
        mock_db = Mock()
        mock_db.scalar.return_value = None

        repo = NotesRepository(mock_db)

        # Act
        result = repo.delete(999)

        # Assert
        assert result is False
        mock_db.delete.assert_not_called()

    def test_delete_note_database_error(self):
        # Arrange
        mock_db = Mock()
        now = datetime.now()
        mock_note = Note(
            id=1, title="Test", content="Content", created_at=now, updated_at=now
        )
        mock_db.scalar.return_value = mock_note
        mock_db.delete = Mock()
        mock_db.commit = Mock(side_effect=SQLAlchemyError("DB Error"))
        mock_db.rollback = Mock()

        repo = NotesRepository(mock_db)

        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            repo.delete(1)

        mock_db.rollback.assert_called_once()
