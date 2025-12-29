from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from db.session import Base


class Word(Base):
    __tablename__ = "words"

    word_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, index=True)
    word = Column(String(255), nullable=False)
    meaning = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    memo = Column(Text, nullable=True)
    created_at = Column(
        DateTime, default=datetime.now(ZoneInfo("Asia/Tokyo")), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.now(ZoneInfo("Asia/Tokyo")),
        onupdate=datetime.now(ZoneInfo("Asia/Tokyo")),
        nullable=False,
    )

    __table_args__ = (Index("idx_words_user_word", "user_id", "word"),)
