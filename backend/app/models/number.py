from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base

class Number(Base):
    __tablename__ = "number"

    id = Column(Integer, primary_key=True, index=True)
    number_type = Column(String(50), nullable=False)
    number = Column(String(50), nullable=False, index=True)
    account_sid = Column(String(255), nullable=True)
    auth_token = Column(String(255), nullable=True)
    agente_id = Column(String(255), nullable=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    agent_status = Column(Boolean, default=False)
