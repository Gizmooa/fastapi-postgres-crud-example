import pytest
from datetime import datetime
from pydantic import ValidationError

from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse


@pytest.mark.unit
class TestNoteCreate:
    def test_create_valid(self):
        note = NoteCreate(title="Test", content="Content")

        assert note.title == "Test"
        assert note.content == "Content"

    def test_create_minimal(self):
        note = NoteCreate(title="Test")

        assert note.title == "Test"
        assert note.content == ""

    def test_create_missing_title(self):
        with pytest.raises(ValidationError):
            NoteCreate(content="Content")

    def test_create_empty_title(self):
        with pytest.raises(ValidationError):
            NoteCreate(title="")

    def test_create_title_too_long(self):
        long_title = "a" * 256
        with pytest.raises(ValidationError):
            NoteCreate(title=long_title)

    def test_create_content_too_long(self):
        long_content = "a" * 10001
        with pytest.raises(ValidationError):
            NoteCreate(title="Test", content=long_content)


@pytest.mark.unit
class TestNoteUpdate:
    def test_update_all_fields(self):
        update = NoteUpdate(title="New Title", content="New Content")

        assert update.title == "New Title"
        assert update.content == "New Content"

    def test_update_title_only(self):
        update = NoteUpdate(title="New Title")

        assert update.title == "New Title"
        assert update.content is None

    def test_update_content_only(self):
        update = NoteUpdate(content="New Content")

        assert update.title is None
        assert update.content == "New Content"

    def test_update_empty(self):
        update = NoteUpdate()

        assert update.title is None
        assert update.content is None

    def test_update_empty_title_string(self):
        with pytest.raises(ValidationError):
            NoteUpdate(title="")

    def test_update_title_too_long(self):
        long_title = "a" * 256
        with pytest.raises(ValidationError):
            NoteUpdate(title=long_title)

    def test_update_content_too_long(self):
        long_content = "a" * 10001
        with pytest.raises(ValidationError):
            NoteUpdate(content=long_content)


@pytest.mark.unit
class TestNoteResponse:
    def test_response_valid(self):
        now = datetime.now()
        response = NoteResponse(
            id=1,
            title="Test",
            content="Content",
            created_at=now,
            updated_at=now,
        )

        assert response.id == 1
        assert response.title == "Test"
        assert response.content == "Content"
        assert response.created_at == now
        assert response.updated_at == now

    def test_response_from_dict(self):
        now = datetime.now()
        data = {
            "id": 1,
            "title": "Test",
            "content": "Content",
            "created_at": now,
            "updated_at": now,
        }
        response = NoteResponse(**data)

        assert response.id == 1
        assert response.title == "Test"

    def test_response_missing_fields(self):
        with pytest.raises(ValidationError):
            NoteResponse(id=1, title="Test")
