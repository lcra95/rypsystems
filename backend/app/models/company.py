from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Company(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, index=True)
    document = Column(String(100), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    direction = Column(String(255), nullable=True)
    business = Column(String(255), nullable=True)
    contact_person = Column(String(255), nullable=True)
    contact_number = Column(String(255), nullable=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
