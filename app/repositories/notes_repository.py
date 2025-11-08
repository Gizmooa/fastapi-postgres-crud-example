import logging
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.core.constants import DEFAULT_PAGE_SIZE
from app.repositories.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate, NoteFullUpdate, NoteResponse

logger = logging.getLogger(__name__)


class NotesRepository:
    def __init__(self, db: Session) -> None:
        self.db: Session = db

    def create(self, note_data: NoteCreate) -> NoteResponse:
        """Create a new note in the database.

        Args:
            note_data: Note creation data

        Returns:
            Created note response

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            note: Note = Note(title=note_data.title, content=note_data.content)
            self.db.add(note)
            self.db.commit()
            self.db.refresh(note)
            logger.info(f"Created note with ID: {note.id}")
            return NoteResponse.model_validate(note)
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating note: {e}")
            raise

    def get_all(
        self, skip: int = 0, limit: int = DEFAULT_PAGE_SIZE
    ) -> list[NoteResponse]:
        """Get all notes with pagination, ordered by creation date (newest first).

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of note responses

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            stmt = (
                select(Note).order_by(Note.created_at.desc()).offset(skip).limit(limit)
            )
            notes: list[Note] = list(self.db.scalars(stmt).all())
            return [NoteResponse.model_validate(n) for n in notes]
        except SQLAlchemyError as e:
            logger.error(f"Error fetching notes: {e}")
            raise

    def get_by_id(self, note_id: int) -> NoteResponse | None:
        """Get a note by its ID.

        Args:
            note_id: Note ID

        Returns:
            Note response if found, None otherwise

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            stmt = select(Note).where(Note.id == note_id)
            note: Note | None = self.db.scalar(stmt)
            return NoteResponse.model_validate(note) if note else None
        except SQLAlchemyError as e:
            logger.error(f"Error fetching note {note_id}: {e}")
            raise

    def update(self, note_id: int, note_data: NoteFullUpdate | NoteUpdate) -> NoteResponse | None:
        """Update an existing note.

        Args:
            note_id: Note ID to update
            note_data: Note update data (NoteFullUpdate for full update, NoteUpdate for partial)

        Returns:
            Updated note response if found, None otherwise

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            stmt = select(Note).where(Note.id == note_id)
            note: Note | None = self.db.scalar(stmt)
            if not note:
                return None

            exclude_unset = isinstance(note_data, NoteUpdate)
            update_data = note_data.model_dump(exclude_unset=exclude_unset)
            for field, value in update_data.items():
                setattr(note, field, value)

            self.db.commit()
            self.db.refresh(note)
            logger.info(f"Updated note with ID: {note_id}")
            return NoteResponse.model_validate(note)
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating note {note_id}: {e}")
            raise

    def delete(self, note_id: int) -> bool:
        """Delete a note by its ID.

        Args:
            note_id: Note ID to delete

        Returns:
            True if deleted, False if not found

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            stmt = select(Note).where(Note.id == note_id)
            note: Note | None = self.db.scalar(stmt)
            if not note:
                return False
            self.db.delete(note)
            self.db.commit()
            logger.info(f"Deleted note with ID: {note_id}")
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting note {note_id}: {e}")
            raise
