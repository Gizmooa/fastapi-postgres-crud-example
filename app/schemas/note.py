from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    """Schema for creating and fully updating a new note."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Note title",
        examples=["My First Note"],
    )
    content: str = Field(
        default="",
        max_length=10000,
        description="Note content",
        examples=["This is the content of my note"],
    )


class NoteUpdate(BaseModel):
    """Schema for updating an existing note (partial update)."""

    title: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="Note title",
        examples=["Updated Note Title"],
    )
    content: str | None = Field(
        None,
        max_length=10000,
        description="Note content",
        examples=["Updated note content"],
    )


class NoteResponse(BaseModel):
    """Schema for note response."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Note ID", examples=[1])
    title: str = Field(..., description="Note title", examples=["My First Note"])
    content: str = Field(
        ..., description="Note content", examples=["Note content here"]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when note was created",
        examples=["2024-01-01T12:00:00Z"],
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when note was last updated",
        examples=["2024-01-01T12:00:00Z"],
    )
