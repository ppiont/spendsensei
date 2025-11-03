"""Content model for SpendSense"""

from datetime import datetime
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from spendsense.database import Base


class Content(Base):
    """Educational content catalog with persona and signal tagging"""

    __tablename__ = "content"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'article', 'video', 'tool'
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    persona_tags: Mapped[str] = mapped_column(
        String(500), nullable=False
    )  # JSON stored as text, list of persona types
    signal_tags: Mapped[str] = mapped_column(
        String(500), nullable=False
    )  # JSON stored as text, list of signal names
    source: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'template', 'llm', 'human'
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    def __repr__(self) -> str:
        return f"<Content(id={self.id}, type={self.type}, title={self.title})>"
