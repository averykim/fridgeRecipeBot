from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class LogStatus(enum.Enum):
    PENDING = "pending" # Before handling by LLM
    RESOLVED = "resolved" # Updated ingredient and ingredient_alias
    FAILED = "failed" # LLM fails to analyze
    

class UnparsedLog(Base):
    __tablename__ = "unparsed_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    raw_text: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(100))
    status: Mapped[LogStatus] = mapped_column(default=LogStatus.PENDING)
    
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    resolved_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)