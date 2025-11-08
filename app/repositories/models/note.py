from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime
from sqlalchemy.sql import func
from app.config.db_settings import Base


class Note(Base):
    """Note database model.

    Attributes:
        id: Primary key
        title: Note title (indexed, max 255 chars)
        content: Note content (optional, max 10000 chars)
        created_at: Timestamp when note was created
        updated_at: Timestamp when note was last updated
    """

    __tablename__ = "notes"

    id: Column[int] = Column(Integer, primary_key=True, index=True)
    title: Column[str] = Column(String(255), nullable=False, index=True)
    content: Column[str] = Column(Text, nullable=True)
    created_at: Column[datetime] = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Column[datetime] = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        title_preview = self.title[:30] + "..." if len(self.title) > 30 else self.title
        return f"<Note(id={self.id}, title='{title_preview}')>"
