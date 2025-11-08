from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.config.db_settings import get_db
from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, MIN_PAGE_SIZE
from app.repositories.notes_repository import NotesRepository
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse

router = APIRouter(prefix="/notes", tags=["notes", "v1"])


def get_notes_repo(db: Session = Depends(get_db)) -> NotesRepository:
    return NotesRepository(db)


@router.post(
    "/",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new note",
    description="Create a new note with title and content",
)
def create_note(
    note_data: NoteCreate,
    repo: NotesRepository = Depends(get_notes_repo),
) -> NoteResponse:
    return repo.create(note_data)


@router.get(
    "/",
    response_model=list[NoteResponse],
    summary="List all notes",
    description="Get a paginated list of all notes",
)
def list_notes(
    skip: Annotated[int, Query(ge=0, description="Number of records to skip")] = 0,
    limit: Annotated[
        int,
        Query(
            ge=MIN_PAGE_SIZE, le=MAX_PAGE_SIZE, description="Maximum number of records"
        ),
    ] = DEFAULT_PAGE_SIZE,
    repo: NotesRepository = Depends(get_notes_repo),
) -> list[NoteResponse]:
    return repo.get_all(skip=skip, limit=limit)


@router.get(
    "/{note_id}",
    response_model=NoteResponse,
    summary="Get a note by ID",
    description="Retrieve a specific note by its ID",
)
def get_note(
    note_id: int,
    repo: NotesRepository = Depends(get_notes_repo),
) -> NoteResponse:
    note: NoteResponse | None = repo.get_by_id(note_id)

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID {note_id} not found",
        )

    return note


@router.put(
    "/{note_id}",
    response_model=NoteResponse,
    summary="Update a note",
    description="Update an existing note (full update - all fields required)",
)
def update_note(
    note_id: int,
    note_data: NoteCreate,
    repo: NotesRepository = Depends(get_notes_repo),
) -> NoteResponse:
    """Update a note with full replacement (all fields required).

    Args:
        note_id: Note ID to update
        note_data: Full note data (all fields required)
        repo: Notes repository dependency

    Returns:
        Updated note response

    Raises:
        HTTPException: If note not found
    """
    updated_note: NoteResponse | None = repo.update(note_id, note_data)

    if not updated_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID {note_id} not found",
        )

    return updated_note


@router.patch(
    "/{note_id}",
    response_model=NoteResponse,
    summary="Partially update a note",
    description="Partially update an existing note (only provided fields will be updated)",
)
def patch_note(
    note_id: int,
    note_data: NoteUpdate,
    repo: NotesRepository = Depends(get_notes_repo),
) -> NoteResponse:
    updated_note: NoteResponse | None = repo.update(note_id, note_data)

    if not updated_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID {note_id} not found",
        )

    return updated_note


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a note",
    description="Delete a note by its ID",
)
def delete_note(
    note_id: int,
    repo: NotesRepository = Depends(get_notes_repo),
) -> None:
    deleted: bool = repo.delete(note_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID {note_id} not found",
        )
