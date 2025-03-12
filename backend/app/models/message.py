from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, index=True)
    to = Column(String(50), nullable=False)
    from_ = Column("from", String(50), nullable=False)
    direction = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)  # <-- Nuevo campo agregado
    number_id = Column(Integer, ForeignKey("number.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
