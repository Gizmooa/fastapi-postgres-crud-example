import pytest
from sqlalchemy.orm import Session

from app.repositories.notes_repository import NotesRepository
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse
from app.repositories.models.note import Note


@pytest.mark.integration
class TestNotesRepositoryCreate:
    def test_create_note_success(self, db_session: Session):
        repo = NotesRepository(db_session)
        note_data = NoteCreate(title="Test Note", content="Test Content")

        result = repo.create(note_data)

        assert isinstance(result, NoteResponse)
        assert result.title == "Test Note"
        assert result.content == "Test Content"
        assert result.id is not None

        db_note = db_session.query(Note).filter(Note.id == result.id).first()
        assert db_note is not None
        assert db_note.title == "Test Note"

    def test_create_note_minimal(self, db_session: Session):
        repo = NotesRepository(db_session)
        note_data = NoteCreate(title="Minimal")

        result = repo.create(note_data)

        assert result.title == "Minimal"
        assert result.content == ""


@pytest.mark.integration
class TestNotesRepositoryGetAll:
    def test_get_all_empty(self, db_session: Session):
        repo = NotesRepository(db_session)

        result = repo.get_all()

        assert result == []

    def test_get_all_single(self, db_session: Session):
        note = Note(title="Test", content="Content")
        db_session.add(note)
        db_session.commit()

        repo = NotesRepository(db_session)
        result = repo.get_all()

        assert len(result) == 1
        assert result[0].title == "Test"

    def test_get_all_multiple(self, db_session: Session):
        for i in range(5):
            note = Note(title=f"Note {i}", content=f"Content {i}")
            db_session.add(note)
        db_session.commit()

        repo = NotesRepository(db_session)
        result = repo.get_all()

        assert len(result) == 5

    def test_get_all_pagination_skip(self, db_session: Session):
        for i in range(5):
            note = Note(title=f"Note {i}", content=f"Content {i}")
            db_session.add(note)
        db_session.commit()

        repo = NotesRepository(db_session)
        result = repo.get_all(skip=2)

        assert len(result) == 3

    def test_get_all_pagination_limit(self, db_session: Session):
        for i in range(5):
            note = Note(title=f"Note {i}", content=f"Content {i}")
            db_session.add(note)
        db_session.commit()

        repo = NotesRepository(db_session)
        result = repo.get_all(limit=2)

        assert len(result) == 2

    def test_get_all_pagination_both(self, db_session: Session):
        for i in range(5):
            note = Note(title=f"Note {i}", content=f"Content {i}")
            db_session.add(note)
        db_session.commit()

        repo = NotesRepository(db_session)
        result = repo.get_all(skip=1, limit=2)

        assert len(result) == 2


@pytest.mark.integration
class TestNotesRepositoryGetById:
    def test_get_by_id_success(self, db_session: Session):
        note = Note(title="Test", content="Content")
        db_session.add(note)
        db_session.commit()
        db_session.refresh(note)

        repo = NotesRepository(db_session)
        result = repo.get_by_id(note.id)

        assert result is not None
        assert isinstance(result, NoteResponse)
        assert result.id == note.id
        assert result.title == "Test"

    def test_get_by_id_not_found(self, db_session: Session):
        repo = NotesRepository(db_session)
        result = repo.get_by_id(999)

        assert result is None


@pytest.mark.integration
class TestNotesRepositoryUpdate:
    def test_update_note_success(self, db_session: Session):
        note = Note(title="Original", content="Original Content")
        db_session.add(note)
        db_session.commit()
        db_session.refresh(note)

        repo = NotesRepository(db_session)
        update_data = NoteUpdate(title="Updated", content="Updated Content")
        result = repo.update(note.id, update_data)

        assert result is not None
        assert result.title == "Updated"
        assert result.content == "Updated Content"

        db_note = db_session.query(Note).filter(Note.id == note.id).first()
        assert db_note.title == "Updated"

    def test_update_note_partial_title(self, db_session: Session):
        note = Note(title="Original", content="Original Content")
        db_session.add(note)
        db_session.commit()
        db_session.refresh(note)

        repo = NotesRepository(db_session)
        update_data = NoteUpdate(title="Updated")
        result = repo.update(note.id, update_data)

        assert result is not None
        assert result.title == "Updated"
        assert result.content == "Original Content"

    def test_update_note_partial_content(self, db_session: Session):
        note = Note(title="Original", content="Original Content")
        db_session.add(note)
        db_session.commit()
        db_session.refresh(note)

        repo = NotesRepository(db_session)
        update_data = NoteUpdate(content="Updated Content")
        result = repo.update(note.id, update_data)

        assert result is not None
        assert result.title == "Original"
        assert result.content == "Updated Content"

    def test_update_note_empty(self, db_session: Session):
        note = Note(title="Original", content="Original Content")
        db_session.add(note)
        db_session.commit()
        db_session.refresh(note)

        repo = NotesRepository(db_session)
        update_data = NoteUpdate()
        result = repo.update(note.id, update_data)

        assert result is not None
        assert result.title == "Original"
        assert result.content == "Original Content"

    def test_update_note_not_found(self, db_session: Session):
        repo = NotesRepository(db_session)
        update_data = NoteUpdate(title="Updated")
        result = repo.update(999, update_data)

        assert result is None


@pytest.mark.integration
class TestNotesRepositoryDelete:
    def test_delete_note_success(self, db_session: Session):
        note = Note(title="Test", content="Content")
        db_session.add(note)
        db_session.commit()
        db_session.refresh(note)
        note_id = note.id

        repo = NotesRepository(db_session)
        result = repo.delete(note_id)

        assert result is True

        db_note = db_session.query(Note).filter(Note.id == note_id).first()
        assert db_note is None

    def test_delete_note_not_found(self, db_session: Session):
        repo = NotesRepository(db_session)
        result = repo.delete(999)

        assert result is False
